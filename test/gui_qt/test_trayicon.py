from types import SimpleNamespace

from plover.gui_qt import trayicon
from plover.gui_qt.trayicon import ModalDictionaryTrayIcon


class FakeSystemTrayIcon:
    @staticmethod
    def isSystemTrayAvailable():
        return True

    def __init__(self):
        self.icon = None
        self.tooltip = None
        self.visible = False

    def setIcon(self, icon):
        self.icon = icon

    def setToolTip(self, tooltip):
        self.tooltip = tooltip

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False


def test_modal_dictionary_tray_icon_tracks_runtime_state(monkeypatch):
    monkeypatch.setattr(trayicon, "QSystemTrayIcon", FakeSystemTrayIcon)
    icon = ModalDictionaryTrayIcon()
    icon.enable()

    modal_dictionary = SimpleNamespace(
        path="plover\\lapwing-movement.modal", enabled=False, _activated=False
    )
    unrelated_dictionary = SimpleNamespace(
        path="unrelated.modal", enabled=True, _activated=True
    )

    icon.update_dictionaries([unrelated_dictionary])
    assert icon._trayicon.tooltip == "Modal dictionary is disabled"
    assert icon._trayicon.icon is icon._state_icons["disabled"]

    modal_dictionary._activated = True
    icon.update_dictionaries([modal_dictionary])
    assert icon._trayicon.tooltip == "Modal dictionary is enabled"
    assert icon._trayicon.icon is icon._state_icons["enabled"]

    modal_dictionary._activated = False
    icon.update_dictionaries([modal_dictionary])
    assert icon._trayicon.tooltip == "Modal dictionary is disabled"
    assert icon._trayicon.icon is icon._state_icons["disabled"]
