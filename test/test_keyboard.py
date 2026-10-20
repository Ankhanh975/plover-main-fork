import pytest

from plover import system
from plover.machine.keyboard import Keyboard
from plover.machine.keymap import Keymap
from plover.oslayer.keyboardcontrol import KeyboardCapture

from unittest import mock


def send_input(capture, key_events):
    for evt in key_events.strip().split():
        if evt.startswith("+"):
            capture.key_down(evt[1:])
        elif evt.startswith("-"):
            capture.key_up(evt[1:])
        else:
            capture.key_down(evt)
            capture.key_up(evt)


@pytest.fixture
def capture():
    capture = mock.MagicMock(spec=KeyboardCapture)
    with mock.patch("plover.machine.keyboard.KeyboardCapture", new=lambda: capture):
        yield capture


@pytest.fixture
def timers(monkeypatch):
    timers = []

    class FakeTimer:
        def __init__(self, interval, callback, args=()):
            self.interval = interval
            self.callback = callback
            self.args = args
            self.daemon = False
            timers.append(self)

        def start(self):
            pass

        def cancel(self):
            pass

        def fire(self):
            self.callback(*self.args)

    monkeypatch.setattr("plover.machine.keyboard.threading.Timer", FakeTimer)
    return timers


@pytest.fixture(params=[{"arpeggiate": False, "first_up_chord_send": False}])
def machine(request, capture):
    machine = Keyboard(request.param)
    keymap = Keymap(Keyboard.KEYS_LAYOUT.split(), system.KEYS + Keyboard.ACTIONS)
    keymap.set_mappings(system.KEYMAPS["Keyboard"])
    machine.set_keymap(keymap)
    return machine


arpeggiate = pytest.mark.parametrize(
    "machine", [{"arpeggiate": True, "first_up_chord_send": False}], indirect=True
)
first_up_chord_send = pytest.mark.parametrize(
    "machine", [{"arpeggiate": False, "first_up_chord_send": True}], indirect=True
)
"""
These are decorators to be applied on test functions to modify the machine configuration.
Note that at the moment it's not possible to apply both at the same time.
"""


@pytest.fixture
def strokes(machine):
    strokes = []
    machine.add_stroke_callback(strokes.append)
    return strokes


def test_lifecycle(capture, machine, strokes):
    # Start machine.
    machine.start_capture()
    assert capture.mock_calls == [
        mock.call.start(),
        mock.call.suppress({"caps_lock"}),
    ]
    capture.reset_mock()
    machine.set_suppression(True)
    suppressed_keys = {"caps_lock", *machine._bindings}
    assert strokes == []
    assert capture.mock_calls == [
        mock.call.suppress(suppressed_keys),
    ]
    # Trigger some strokes.
    capture.reset_mock()
    send_input(capture, "+a +h -a -h space w")
    assert strokes == [
        {"S-", "*"},
        {"T-"},
    ]
    assert capture.mock_calls == []
    # Stop machine.
    del strokes[:]
    machine.stop_capture()
    assert strokes == []
    assert capture.mock_calls == [
        mock.call.suppress({"caps_lock"}),
        mock.call.cancel(),
    ]


def test_caps_lock_toggles_output_without_becoming_a_stroke(capture, machine, strokes):
    commands = []
    machine.add_command_callback(commands.append)
    machine.start_capture()

    send_input(capture, "caps_lock")

    assert commands == ["toggle"]
    assert strokes == []


def test_no_op_keys_are_not_suppressed_or_translated(capture, machine, strokes):
    machine.start_capture()
    machine.set_suppression(True)

    suppressed_keys = capture.suppress.call_args.args[0]
    assert "," not in suppressed_keys
    assert "." not in suppressed_keys

    send_input(capture, ", .")

    assert strokes == []


def test_unbound_edit_keys_are_reported(capture, machine):
    edits = []
    machine.add_key_callback(edits.append)
    machine.start_capture()
    machine.set_suppression(True)

    send_input(capture, "BackSpace Delete")

    assert edits == ["BackSpace", "Delete"]


def test_unfinished_stroke_1(capture, machine, strokes):
    machine.start_capture()
    send_input(capture, "+a +q -a")
    assert strokes == []


def test_unfinished_stroke_2(capture, machine, strokes):
    machine.start_capture()
    send_input(capture, "+a +r -a +a -r")
    assert strokes == []


def test_stroke_is_sent_after_key_down_quiet_period(capture, machine, strokes, timers):
    machine.start_capture()
    capture.key_down("a")

    assert strokes == []
    assert timers[-1].interval == machine.KEY_DOWN_DELAY
    timers[-1].fire()
    assert strokes == [{"S-"}]

    capture.key_up("a")
    assert strokes == [{"S-"}]


def test_early_stroke_is_replaced_when_chord_grows(capture, machine, strokes, timers):
    machine.start_capture()
    capture.key_down("a")
    timers[-1].fire()
    capture.key_down("h")
    timers[-1].fire()

    assert strokes == [{"S-"}, {"*"}, {"S-", "*"}]

    capture.key_up("a")
    capture.key_up("h")
    assert strokes == [{"S-"}, {"*"}, {"S-", "*"}]


def test_undo_stroke_is_not_sent_early_before_chord_growth(
    capture, machine, strokes, timers
):
    machine.start_capture()
    undo_key = next(
        key
        for key, steno_key in machine._bindings.items()
        if steno_key in system.Stroke.UNDO_STROKE.steno_keys
    )
    other_key = next(
        key
        for key, steno_key in machine._bindings.items()
        if steno_key is not None and steno_key not in system.Stroke.UNDO_STROKE.steno_keys
    )
    expected_stroke = {
        machine._bindings[undo_key],
        machine._bindings[other_key],
    }

    capture.key_down(undo_key)
    timers[-1].fire()
    assert strokes == []

    capture.key_down(other_key)
    timers[-1].fire()
    assert strokes == [expected_stroke]

    capture.key_up(undo_key)
    capture.key_up(other_key)
    assert strokes == [expected_stroke]


def test_chord_growth_is_corrected_if_released_before_quiet_period(
    capture, machine, strokes, timers
):
    machine.start_capture()
    capture.key_down("a")
    timers[-1].fire()
    capture.key_down("h")
    capture.key_up("a")
    capture.key_up("h")

    assert strokes == [{"S-"}, {"*"}, {"S-", "*"}]


def test_keys_pressed_before_quiet_period_are_sent_as_one_stroke(
    capture, machine, strokes, timers
):
    machine.start_capture()
    capture.key_down("a")
    first_timer = timers[-1]
    capture.key_down("h")
    timers[-1].fire()
    first_timer.fire()

    assert strokes == [{"S-", "*"}]


def test_released_stroke_is_not_undone_by_next_stroke(capture, machine, strokes, timers):
    machine.start_capture()
    capture.key_down("a")
    timers[-1].fire()
    capture.key_up("a")

    capture.key_down("h")
    timers[-1].fire()
    assert strokes == [{"S-"}]

    capture.key_up("h")
    assert strokes == [{"S-"}, {"*"}]


@pytest.mark.parametrize(
    "machine",
    [
        {
            "arpeggiate": False,
            "first_up_chord_send": False,
            "early_stroke_send": False,
        }
    ],
    indirect=True,
)
def test_early_chord_send_can_be_disabled(capture, machine, strokes, timers):
    machine.start_capture()
    capture.key_down("a")
    capture.key_down("h")

    assert timers == []
    assert strokes == []

    capture.key_up("a")
    assert strokes == []

    capture.key_up("h")
    assert strokes == [{"S-", "*"}]


@arpeggiate
def test_arpeggiate_1(capture, machine, strokes):
    machine.start_capture()
    send_input(capture, "a h space w")
    assert strokes == [{"S-", "*"}]


@arpeggiate
def test_arpeggiate_2(capture, machine, strokes):
    machine.start_capture()
    send_input(capture, "a +h +space -space -h w")
    assert strokes == [{"S-", "*"}]


@first_up_chord_send
def test_first_up_chord_send(capture, machine, strokes):
    machine.start_capture()
    send_input(capture, "+a +w +l -l +l")
    assert strokes == [{"S-", "T-", "-G"}]
    send_input(capture, "-l")
    assert strokes == [{"S-", "T-", "-G"}, {"S-", "T-", "-G"}]
    send_input(capture, "-a -w")
    assert strokes == [{"S-", "T-", "-G"}, {"S-", "T-", "-G"}]
