from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from plover.gui_qt.engine import Engine as QtEngine
from plover.gui_qt.key_event_timeline import KeyEventModel, KeyEventTimeline
from plover.registry import registry


def test_key_event_model_shows_edges_and_held_duration():
    app = QApplication.instance() or QApplication([])
    model = KeyEventModel()

    model.add_event("a", "down", 10.0)
    model.add_event("b", "down", 10.1)
    model.add_event("a", "up", 10.25)
    model.add_event("b", "up", 10.5)

    assert model.rowCount() == 4
    assert model.data(model.index(0, 0)) == "+0.000000 s"
    assert model.data(model.index(0, 1)) == "a"
    assert model.data(model.index(0, 2)) == "Down"
    assert model.data(model.index(2, 2)) == "Up"
    assert model.data(model.index(2, 3)) == "0.250000 s"
    assert model.data(model.index(3, 3)) == "0.400000 s"
    assert model.data(model.index(0, 2), Qt.ItemDataRole.BackgroundRole).isValid()
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Elapsed time"

    model.clear()

    assert model.rowCount() == 0
    assert model._pressed == {}
    assert app is not None


def test_key_event_timeline_is_registered_and_receives_events():
    app = QApplication.instance() or QApplication([])
    callbacks = {}
    assert hasattr(QtEngine, "signal_key_event")

    class Engine:
        def signal_connect(self, name, callback):
            callbacks[name] = callback

    timeline = KeyEventTimeline(Engine())
    callbacks["key_event"]("a", "down", 1.0)
    callbacks["key_event"]("a", "up", 1.2)

    assert timeline._model.rowCount() == 2
    assert timeline._model.data(timeline._model.index(1, 2)) == "Up"
    assert any(
        plugin.name == "key_event_timeline"
        for plugin in registry.list_plugins("gui.qt.tool")
    )
    timeline.close()
    assert app is not None