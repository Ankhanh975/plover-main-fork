from collections import deque
from queue import Empty

import pytest

from plover import system
from plover.machine.keymap import Keymap
from plover.machine.plover_hid import PloverHid, STENO_KEY_CHART


class TimedReportQueue:
    def __init__(self, clock, reports):
        self.clock = clock
        self.reports = deque(reports)

    def get(self, timeout):
        deadline = self.clock[0] + timeout
        if self.reports and self.reports[0][0] <= deadline:
            report_time, report = self.reports.popleft()
            self.clock[0] = report_time
            return report
        self.clock[0] = deadline
        raise Empty


def report_for_keys(*keys):
    key_state = 0
    for key in keys:
        key_state |= 1 << (63 - STENO_KEY_CHART.index(key))
    return b"\x50" + key_state.to_bytes(8, "big")


@pytest.fixture
def hid_machine(monkeypatch):
    params = {
        "first_up_chord_send": False,
        "early_stroke_send": True,
        "double_tap_repeat": False,
        "repeat_delay_ms": 200,
        "repeat_interval_ms": 30,
        "device_scan_interval_ms": 1000,
    }
    machine = PloverHid(params)
    keymap = Keymap(PloverHid.get_keys(), system.KEYS)
    keymap.set_mappings(system.KEYMAPS["Plover HID"])
    machine.set_keymap(keymap)

    clock = [0.0]
    monkeypatch.setattr("plover.machine.plover_hid.time.monotonic", lambda: clock[0])
    monkeypatch.setattr("plover.machine.plover_hid.time.time", lambda: clock[0])

    wait_count = 0

    def finished_wait(timeout):
        nonlocal wait_count
        wait_count += 1
        return wait_count > 30

    monkeypatch.setattr(machine.finished, "wait", finished_wait)
    machine._report_queue = TimedReportQueue(clock, [])
    return machine, clock


def run_reports(machine, clock, reports, include_times=False):
    machine._report_queue = TimedReportQueue(clock, reports)
    strokes = []

    def on_stroke(stroke):
        stroke = set(stroke)
        if include_times:
            strokes.append((clock[0], stroke))
        else:
            strokes.append(stroke)

    machine.add_stroke_callback(on_stroke)
    machine.run()
    return strokes


def test_early_chord_send_after_quiet_period(hid_machine):
    machine, clock = hid_machine

    strokes = run_reports(
        machine,
        clock,
        [(0.0, report_for_keys("S1-")), (0.1, report_for_keys())],
        include_times=True,
    )

    assert strokes == [(machine.EARLY_STROKE_DELAY, {"S-"})]


def test_early_chord_send_corrects_when_chord_grows(hid_machine):
    machine, clock = hid_machine

    strokes = run_reports(
        machine,
        clock,
        [
            (0.0, report_for_keys("S1-")),
            (0.05, report_for_keys("S1-", "T-")),
            (0.06, report_for_keys()),
        ],
    )

    assert strokes == [{"S-"}, {"*"}, {"S-", "T-"}]


def test_undo_stroke_is_not_sent_early(hid_machine):
    machine, clock = hid_machine

    strokes = run_reports(
        machine,
        clock,
        [(0.0, report_for_keys("*1")), (0.1, report_for_keys())],
    )

    assert strokes == [{"*"}]


def test_early_send_does_not_start_double_tap_repeat(hid_machine):
    machine, clock = hid_machine
    machine._params["double_tap_repeat"] = True
    machine._params["repeat_delay_ms"] = 50

    strokes = run_reports(
        machine,
        clock,
        [(0.0, report_for_keys("S1-")), (0.3, report_for_keys())],
    )

    assert strokes == [{"S-"}]


def test_chord_growth_corrects_repeated_provisional_output(hid_machine):
    machine, clock = hid_machine
    machine._params["double_tap_repeat"] = True
    machine._params["repeat_delay_ms"] = 50

    strokes = run_reports(
        machine,
        clock,
        [
            (0.0, report_for_keys("S1-")),
            (0.02, report_for_keys()),
            (0.03, report_for_keys("S1-")),
            (0.1, report_for_keys("S1-", "T-")),
            (0.15, report_for_keys()),
        ],
    )

    assert strokes == [
        {"S-"},
        {"S-"},
        {"S-"},
        {"*"},
        {"*"},
        {"S-", "T-"},
    ]


def test_early_chord_send_can_be_disabled(hid_machine):
    machine, clock = hid_machine
    machine._params["early_stroke_send"] = False

    strokes = run_reports(
        machine,
        clock,
        [(0.0, report_for_keys("S1-")), (0.1, report_for_keys())],
        include_times=True,
    )

    assert strokes == [(0.1, {"S-"})]
