from collections import defaultdict, deque

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableView,
    QVBoxLayout,
)

from plover import _
from plover.gui_qt.tool import Tool


class KeyEventModel(QAbstractTableModel):
    HEADERS = (
        _("Elapsed time"),
        _("Key"),
        _("Edge"),
        _("Held duration"),
    )

    def __init__(self):
        super().__init__()
        self._events = []
        self._first_timestamp = None
        self._pressed = defaultdict(deque)

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._events)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.HEADERS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        key, action, timestamp, held_duration = self._events[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                elapsed = timestamp - self._first_timestamp
                return f"+{elapsed:.6f} s"
            if index.column() == 1:
                return key
            if index.column() == 2:
                return _("Down") if action == "down" else _("Up")
            if index.column() == 3 and held_duration is not None:
                return f"{held_duration:.6f} s"
        elif role == Qt.ItemDataRole.BackgroundRole and index.column() == 2:
            color = "#d9ead3" if action == "down" else "#f4cccc"
            return QColor(color)
        elif role == Qt.ItemDataRole.TextAlignmentRole and index.column() in (0, 3):
            return int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return str(section + 1)

    def add_event(self, key, action, timestamp):
        if action not in ("down", "up"):
            raise ValueError(f"unsupported key event action: {action!r}")

        held_duration = None
        if action == "down":
            self._pressed[key].append(timestamp)
        else:
            pressed = self._pressed.get(key)
            if pressed:
                held_duration = timestamp - pressed.popleft()
                if not pressed:
                    del self._pressed[key]

        if self._first_timestamp is None:
            self._first_timestamp = timestamp
        row = len(self._events)
        self.beginInsertRows(QModelIndex(), row, row)
        self._events.append((key, action, timestamp, held_duration))
        self.endInsertRows()

    def clear(self):
        self.beginResetModel()
        self._events.clear()
        self._first_timestamp = None
        self._pressed.clear()
        self.endResetModel()


class KeyEventTimeline(Tool):
    """Chronological timeline of physical key press and release events."""

    TITLE = _("Key Event Timeline")
    ROLE = "key_event_timeline"

    def __init__(self, engine):
        super().__init__(engine)
        self.resize(660, 400)
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                _(
                    "Each row records a physical key edge. Time is elapsed "
                    "from the first event. This tool is available with the "
                    "Keyboard and Plover HID machines."
                ),
                self,
            )
        )

        self._model = KeyEventModel()
        self._table = QTableView(self)
        self._table.setModel(self._model)
        self._table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

        buttons = QHBoxLayout()
        buttons.addStretch()
        self._clear_button = QPushButton(_("Clear"), self)
        self._clear_button.clicked.connect(self._model.clear)
        buttons.addWidget(self._clear_button)
        layout.addLayout(buttons)

        engine.signal_connect("key_event", self.handle_key_event)

    @Slot(str, str, float)
    def handle_key_event(self, key, action, timestamp):
        self._model.add_event(key, action, timestamp)
        self._table.scrollToBottom()