# -*- coding: utf-8 -*-
# Copyright (c) 2010 Joshua Harlan Lifton.
# See LICENSE.txt for details.

"For use with a computer keyboard (preferably NKRO) as a steno machine."

import threading

from plover import _, system
from plover.machine.base import StenotypeBase
from plover.misc import boolean
from plover.oslayer.keyboardcontrol import KeyboardCapture


# i18n: Machine name.
_._("Keyboard")


class Keyboard(StenotypeBase):
    """Standard stenotype interface for a computer keyboard.

    This class implements the three methods necessary for a standard
    stenotype interface: start_capture, stop_capture, and
    add_callback.

    """

    KEYS_LAYOUT = """
    Escape  F1 F2 F3 F4  F5 F6 F7 F8  F9 F10 F11 F12

      `  1  2  3  4  5  6  7  8  9  0  -  =  \\ BackSpace  Insert Home Page_Up
     Tab  q  w  e  r  t  y  u  i  o  p  [  ]               Delete End  Page_Down
           a  s  d  f  g  h  j  k  l  ;  '      Return
            z  x  c  v  b  n  m  ,  .  /                          Up
                     space                                   Left Down Right
    """
    ACTIONS = ("arpeggiate",)
    KEY_DOWN_DELAY = 0.035

    # Map Windows VK codes for modifier notification to canonical names.
    VK_TO_MODNAME = {
        0xA2: "Control",
        0xA3: "Control",
        0xA0: "Shift",
        0xA1: "Shift",
        0xA4: "Alt",
        0xA5: "Alt",
        0x5B: "Win",
        0x5C: "Win",
    }

    def __init__(self, params):
        """Monitor the keyboard's events."""
        super().__init__()
        self._arpeggiate = params["arpeggiate"]
        self._first_up_chord_send = params["first_up_chord_send"]
        self._early_stroke_send = params.get("early_stroke_send", True)
        self._always_suppressed_keys = {"caps_lock"}
        if self._arpeggiate and self._first_up_chord_send:
            self._error()
            raise RuntimeError(
                "Arpeggiate and first-up chord send cannot both be enabled!"
            )
        self._is_suppressed = False
        self._stroke_lock = threading.RLock()
        self._stroke_timer = None
        self._stroke_timer_generation = 0
        self._early_stroke_sent = False
        self._stroke_needs_correction = False
        # Currently held keys.
        self._down_keys = set()
        if self._first_up_chord_send:
            # If this is True, the first key in a stroke has already been released
            # and subsequent key-up events should not send more strokes
            self._chord_already_sent = False
        else:
            # Collect the keys in the stroke, in case first_up_chord_send is False
            self._stroke_keys = set()
        self._keyboard_capture = None
        self._last_stroke_key_down_count = 0
        self._stroke_key_down_count = 0
        self._update_bindings()

    def _update_suppression(self):
        if self._keyboard_capture is None:
            return
        suppressed_keys = set(self._always_suppressed_keys)
        if self._is_suppressed:
            suppressed_keys.update(self._bindings.keys())
        self._keyboard_capture.suppress(suppressed_keys)

    def _update_bindings(self):
        self._arpeggiate_key = None
        self._bindings = dict(self.keymap.get_bindings())
        for key, mapping in list(self._bindings.items()):
            if "no-op" == mapping:
                del self._bindings[key]
            elif "arpeggiate" == mapping:
                if self._arpeggiate:
                    self._bindings[key] = None
                    self._arpeggiate_key = key
                else:
                    # Don't suppress arpeggiate key if it's not used.
                    del self._bindings[key]
        self._update_suppression()

    def set_keymap(self, keymap):
        super().set_keymap(keymap)
        self._update_bindings()

    def start_capture(self):
        """Begin listening for output from the stenotype machine."""
        self._initializing()
        try:
            self._keyboard_capture = KeyboardCapture()
            self._keyboard_capture.key_down = self._key_down
            self._keyboard_capture.key_up = self._key_up
            # Receive modifier state changes from the capture layer.
            try:
                self._keyboard_capture.modifier_callback = self._modifier_changed
            except Exception:
                # Older capture implementations may not support this attribute.
                pass
            self._keyboard_capture.start()
            self._update_suppression()
        except:
            self._error()
            raise
        self._ready()

    def stop_capture(self):
        """Stop listening for output from the stenotype machine."""
        with self._stroke_lock:
            self._cancel_stroke_timer()
        if self._keyboard_capture is not None:
            self._is_suppressed = False
            self._update_suppression()
            self._keyboard_capture.cancel()
            self._keyboard_capture = None
        self._stopped()

    def set_suppression(self, enabled):
        self._is_suppressed = enabled
        self._update_suppression()

    def suppress_last_stroke(self, send_backspaces):
        send_backspaces(self._last_stroke_key_down_count)
        self._last_stroke_key_down_count = 0

    def _cancel_stroke_timer(self):
        self._stroke_timer_generation += 1
        if self._stroke_timer is not None:
            self._stroke_timer.cancel()
            self._stroke_timer = None

    def _schedule_stroke(self):
        self._cancel_stroke_timer()
        generation = self._stroke_timer_generation
        self._stroke_timer = threading.Timer(
            self.KEY_DOWN_DELAY, self._send_early_stroke, args=(generation,)
        )
        self._stroke_timer.daemon = True
        self._stroke_timer.start()

    def _steno_keys_for_stroke(self):
        return {self._bindings.get(key) for key in self._stroke_keys} - {None}

    def _notify_correction(self):
        self._notify(set(system.Stroke.UNDO_STROKE.steno_keys))

    def _send_early_stroke(self, generation):
        with self._stroke_lock:
            if generation != self._stroke_timer_generation:
                return
            self._stroke_timer = None
            if (
                self._first_up_chord_send
                or not self._down_keys
                or not self._stroke_keys
                or (
                    self._arpeggiate
                    and self._arpeggiate_key not in self._stroke_keys
                )
            ):
                return

            steno_keys = self._steno_keys_for_stroke()
            if not steno_keys:
                return
            if not self._early_stroke_send:
                return
            if (
                not self._early_stroke_sent
                and steno_keys == set(system.Stroke.UNDO_STROKE.steno_keys)
            ):
                return
            if self._stroke_needs_correction:
                self._notify_correction()
            self._last_stroke_key_down_count = self._stroke_key_down_count
            self._notify(steno_keys)
            self._early_stroke_sent = True
            self._stroke_needs_correction = False

    def _key_down(self, key):
        """Called when a key is pressed."""
        assert key is not None
        if key == "caps_lock":
            self._notify_command("toggle")
            return
        if key not in self._bindings:
            if key in ("BackSpace", "Delete"):
                self._notify_key(key)
            return
        with self._stroke_lock:
            is_new_key = key not in self._down_keys
            self._stroke_key_down_count += 1
            self._down_keys.add(key)
            if self._first_up_chord_send:
                self._chord_already_sent = False
            else:
                self._stroke_keys.add(key)
                if is_new_key and self._early_stroke_send:
                    if self._early_stroke_sent:
                        self._stroke_needs_correction = True
                    self._schedule_stroke()

    def _key_up(self, key):
        """Called when a key is released."""
        assert key is not None
        if key == "caps_lock":
            return
        if key not in self._bindings:
            return

        with self._stroke_lock:
            self._down_keys.discard(key)

            if self._first_up_chord_send:
                if self._chord_already_sent:
                    return
            else:
                # A stroke is complete if all pressed keys have been released,
                # and — when arpeggiate mode is enabled — the arpeggiate key
                # is part of it.
                if (
                    self._down_keys
                    or not self._stroke_keys
                    or (
                        self._arpeggiate
                        and self._arpeggiate_key not in self._stroke_keys
                    )
                ):
                    return

            self._cancel_stroke_timer()
            self._last_stroke_key_down_count = self._stroke_key_down_count
            if self._first_up_chord_send:
                steno_keys = {self._bindings.get(k) for k in self._down_keys | {key}}
                self._chord_already_sent = True
            else:
                steno_keys = self._steno_keys_for_stroke()
                needs_correction = self._stroke_needs_correction
                if needs_correction:
                    self._notify_correction()
                self._stroke_keys.clear()
                if (not self._early_stroke_sent or needs_correction) and steno_keys:
                    self._notify(steno_keys)
            if self._first_up_chord_send:
                steno_keys -= {None}
                if steno_keys:
                    self._notify(steno_keys)
            self._early_stroke_sent = False
            self._stroke_needs_correction = False
            self._stroke_key_down_count = 0

    def _modifier_changed(self, vk_codes):
        """Called by the capture layer when modifier keys change.

        vk_codes is an iterable of virtual-key codes currently held.
        """
        mods = set()
        for vk in set(vk_codes or []):
            name = self.VK_TO_MODNAME.get(vk)
            if name:
                mods.add(name)
        from plover import log

        log.info("Modifiers detected: %s (from VK codes: %s)", mods, vk_codes)
        # Notify subscribers on the machine base about modifier set.
        self._notify_modifier(mods)

    @classmethod
    def get_option_info(cls):
        return {
            "arpeggiate": (False, boolean),
            "first_up_chord_send": (False, boolean),
            "early_stroke_send": (True, boolean),
        }
