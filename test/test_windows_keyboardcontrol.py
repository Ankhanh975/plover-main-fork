import sys
from types import SimpleNamespace
from unittest import mock

import pytest

if sys.platform != "win32":
    pytest.skip("Windows keyboard emulation tests", allow_module_level=True)

from plover.oslayer.windows.keyboardcontrol import (
    KEYEVENTF_KEYUP,
    KEYEVENTF_UNICODE,
    KeyboardEmulation,
)  # noqa: E402


@pytest.fixture
def keyboard_emulation():
    emulation = KeyboardEmulation.__new__(KeyboardEmulation)
    emulation.keyboard_layout = SimpleNamespace(
        char_to_vk_ss={
            "a": (ord("a"), 0),
            "b": (ord("b"), 0),
            "\x08": (0x08, 0),
        },
        ss_to_vks={0: []},
    )
    emulation._key_press_delay_ms = 0
    emulation._refresh_keyboard_layout = mock.Mock()
    emulation._send_input = mock.Mock()
    return emulation


def _keyboard_events(send_input_call):
    return [
        (event.union.ki.wVk, event.union.ki.wScan, event.union.ki.dwFlags)
        for event in send_input_call.args
    ]


def test_send_string_batches_events(keyboard_emulation):
    keyboard_emulation.send_string("ab")

    keyboard_emulation._send_input.assert_called_once()
    assert _keyboard_events(keyboard_emulation._send_input.call_args) == [
        (ord("a"), 0, 0),
        (ord("a"), 0, KEYEVENTF_KEYUP),
        (ord("b"), 0, 0),
        (ord("b"), 0, KEYEVENTF_KEYUP),
    ]


def test_send_string_batches_unicode_with_mapped_keys(keyboard_emulation):
    keyboard_emulation.send_string("a\u2603")

    keyboard_emulation._send_input.assert_called_once()
    assert _keyboard_events(keyboard_emulation._send_input.call_args) == [
        (ord("a"), 0, 0),
        (ord("a"), 0, KEYEVENTF_KEYUP),
        (0, 0x2603, KEYEVENTF_UNICODE),
        (0, 0x2603, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP),
    ]


def test_send_string_preserves_configured_delay(keyboard_emulation):
    keyboard_emulation._key_press_delay_ms = 1
    keyboard_emulation.delay = mock.Mock()

    keyboard_emulation.send_string("ab")

    assert keyboard_emulation._send_input.call_count == 2
    assert keyboard_emulation.delay.call_count == 2


def test_send_backspaces_batches_events(keyboard_emulation):
    keyboard_emulation.send_backspaces(2)

    keyboard_emulation._send_input.assert_called_once()
    assert _keyboard_events(keyboard_emulation._send_input.call_args) == [
        (0x08, 0, 0),
        (0x08, 0, KEYEVENTF_KEYUP),
        (0x08, 0, 0),
        (0x08, 0, KEYEVENTF_KEYUP),
    ]
