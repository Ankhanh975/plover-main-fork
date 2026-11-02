from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QMainWindow,
    QSizePolicy,
    QVBoxLayout,
)
from PySide6.QtCore import QPoint

from plover.gui_qt.main_window import MainWindow
from plover.gui_qt.main_window_ui import Ui_MainWindow


def test_main_window_home_and_dictionary_tabs():
    app = QApplication.instance() or QApplication([])

    class UiHost(QMainWindow):
        def reconnect(self):
            pass

        def configure(self):
            pass

        def open_config_folder(self):
            pass

        def show_window(self):
            pass

        def toggle_output(self, enabled):
            pass

        def open_about_dialog(self):
            pass

        def enable_output(self):
            pass

        def disable_output(self):
            pass

    window = UiHost()
    ui = Ui_MainWindow()
    ui.setupUi(window)

    assert [ui.mainTabs.tabText(i) for i in range(ui.mainTabs.count())] == [
        "Home",
        "Dictionaries",
    ]
    assert ui.dictionaries.parentWidget() is ui.dictionariesTab
    assert ui.disable_multistroke_outlines.text() == "Disable multi-stroke outlines"
    assert ui.early_stroke_send.text() == "Early stroke send"
    assert ui.first_up_chord_send.text() == "Send strokes on first release"
    assert ui.input_method_keyboard.text() == "Keyboard"
    assert ui.input_method_plover_hid.text() == "Plover HID"
    assert ui.space_before_output.text() == "Before Output"
    assert ui.space_after_output.text() == "After Output"
    assert isinstance(ui.homeLayout, QVBoxLayout)
    assert ui.homeLayout.spacing() == 6
    assert [
        ui.homeLayout.itemAt(index).widget()
        for index in range(ui.homeLayout.count() - 1)
    ] == [ui.outputGroup, ui.machineGroup, ui.stenoOptionsGroup]
    bottom_spacer = ui.homeLayout.itemAt(ui.homeLayout.count() - 1).spacerItem()
    assert bottom_spacer is not None
    assert bottom_spacer.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Expanding
    for layout in (
        ui.outputGroupLayout,
        ui.inputMethodChoicesLayout,
        ui.spacePlacementChoicesLayout,
    ):
        assert isinstance(layout, QHBoxLayout)
    for layout in (ui.inputMethodChoicesLayout, ui.spacePlacementChoicesLayout):
        assert layout.spacing() == 8
        assert layout.contentsMargins().left() == 0
        assert layout.contentsMargins().top() == 0
    assert ui.input_method_keyboard.parentWidget() is ui.inputMethodChoices
    assert ui.space_before_output.parentWidget() is ui.spacePlacementChoices
    assert ui.inputMethodLabel.parentWidget() is ui.inputMethodRow
    assert ui.machine_state.parentWidget() is ui.machineStatusRow
    assert ui.reconnect_button.parentWidget() is ui.machineStatusRow
    assert ui.reconnect_button.text() == "Reconnect"
    assert [group.title() for group in ui.homeTab.findChildren(QGroupBox)] == [
        "Output",
        "Machine",
        "Steno options",
    ]
    assert ui.output_enable.parentWidget() is ui.outputGroup
    assert ui.output_disable.parentWidget() is ui.outputGroup
    window.resize(650, 450)
    window.show()
    app.processEvents()
    home_widgets = (
        ui.outputGroup,
        ui.machineGroup,
        ui.stenoOptionsGroup,
        ui.inputMethodLabel,
        ui.machine_state,
        ui.reconnect_button,
        ui.disable_multistroke_outlines,
        ui.early_stroke_send,
        ui.first_up_chord_send,
        ui.spacePlacementLabel,
    )
    initial_positions = tuple(
        widget.mapTo(ui.homeTab, QPoint(0, 0)).y() for widget in home_widgets
    )
    window.resize(650, 700)
    app.processEvents()
    expanded_positions = tuple(
        widget.mapTo(ui.homeTab, QPoint(0, 0)).y() for widget in home_widgets
    )
    assert expanded_positions == initial_positions
    assert (
        ui.stenoOptionsGroup.geometry().bottom() <= ui.homeTab.contentsRect().bottom()
    )
    window.close()
    assert app is not None


def test_main_window_quick_settings_update_engine_config():
    app = QApplication.instance() or QApplication([])

    class Engine:
        def __init__(self):
            self.values = {
                "machine_type": "Keyboard",
                "space_placement": "Before Output",
                "disable_multistroke_outlines": False,
                "machine_specific_options": {
                    "early_stroke_send": True,
                    "first_up_chord_send": False,
                },
            }

        @property
        def config(self):
            return self.values

        @config.setter
        def config(self, update):
            self.values.update(update)

    class Window:
        _engine = Engine()

    MainWindow.update_machine_type(Window, "Plover HID")
    MainWindow.update_disable_multistroke_outlines(Window, True)
    MainWindow.update_machine_option(Window, "early_stroke_send", False)
    MainWindow.update_space_placement(Window, "After Output")

    assert Window._engine.config == {
        "machine_type": "Plover HID",
        "space_placement": "After Output",
        "disable_multistroke_outlines": True,
        "machine_specific_options": {
            "early_stroke_send": False,
            "first_up_chord_send": False,
        },
    }
    assert app is not None
