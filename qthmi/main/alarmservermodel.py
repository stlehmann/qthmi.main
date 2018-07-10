"""Model for alarm handling.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2018-06-11 18:16:58
:last modified by:   Stefan Lehmann
:last modified time: 2018-07-10 10:05:34

"""
from typing import Any
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant, QModelIndex, pyqtSignal
from .alarmserver import AlarmServer, AlarmNotDefinedError


ALARM_NR = 0
ALARM_TEXT = 1
ALARM_COUNTER = 2
ALARM_TIME_COMING = 3
ALARM_TIME_GOING = 4
COLUMN_COUNT = 5
TIME_PATTERN = "%H:%M:%S"


class AlarmServerModel(QAbstractTableModel, AlarmServer):
    """Model for access to AlarmServer.

    This class allows the user access to the alarm server via
    the model/view mechanism of the Qt framework.

    """

    dataChanged = pyqtSignal(QModelIndex, QModelIndex)
    alarm_acknowledged = pyqtSignal(int)

    def __init__(self) -> None:
        AlarmServer.__init__(self)
        super(AlarmServerModel, self).__init__()

    def _dataChanged_signal(self, alarm_nr: int) -> None:
        alarm = self.defined_alarms.get(alarm_nr)

        if alarm is None:
            raise AlarmNotDefinedError(alarm_nr)

        if alarm in self.current_alarms:
            row = self.current_alarms.index(alarm)
            indexTopLeft = self.index(row, 0, QModelIndex())
            indexBottomRight = self.index(row, COLUMN_COUNT - 1, QModelIndex())
            self.dataChanged.emit(indexTopLeft, indexBottomRight)

    def acknowledge(self, alarm_nr: int) -> None:
        """Acknowledge the current alarm with the given number.

        Emit a signal 'alarm_acknowledged'.

        """
        AlarmServer.acknowledge(self, alarm_nr)
        self._dataChanged_signal(alarm_nr)
        self.alarm_acknowledged.emit(alarm_nr)

    def acknowledge_all(self) -> None:
        """Acknowledge all current alarms."""
        self.beginResetModel()
        for alarm in self.current_alarms:
            self.acknowledge(alarm.alarm_nr)
        self.endResetModel()

    def alarm_coming(self, alarm_nr: int) -> None:
        """Set the alarm with the given number to active."""
        alarm = self.defined_alarms.get(alarm_nr)
        if alarm is None:
            raise AlarmNotDefinedError(alarm_nr)

        if alarm in self.current_alarms:
            AlarmServer.alarm_coming(self, alarm_nr)
            row = self.current_alarms.index(alarm)
            indexTopLeft = self.index(row, 0, QModelIndex())
            indexBottomRight = self.index(row, COLUMN_COUNT - 1, QModelIndex())

            self.dataChanged.emit(indexTopLeft, indexBottomRight)
        else:
            alarm_count = len(self.current_alarms)
            self.beginInsertRows(QModelIndex(), alarm_count - 1, alarm_count - 1)
            AlarmServer.alarm_coming(self, alarm_nr)
            self.endInsertRows()

    def alarm_going(self, alarm_nr: int) -> None:
        """Set the alarm with the given number to inactive."""
        AlarmServer.alarm_going(self, alarm_nr)
        self._dataChanged_signal(alarm_nr)

    def clear(self, alarm_nr: int) -> None:
        """Clear the given alarm."""
        alarm = self.defined_alarms.get(alarm_nr)
        if alarm is None:
            raise AlarmNotDefinedError(alarm_nr)

        if alarm in self.current_alarms:
            row = self.current_alarms.index(alarm)
            self.beginRemoveRows(QModelIndex(), row, row)
            AlarmServer.clear(self, alarm_nr)
            self.endRemoveRows()

    def clear_all(self) -> None:
        """Clear all current alarms."""
        self.beginResetModel()
        AlarmServer.clear_all(self)
        self.endResetModel()

    def columnCount(self, index: QModelIndex = QModelIndex()) -> int:
        """Return column count."""
        return COLUMN_COUNT

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Return data."""
        if not index.isValid() or not (0 <= index.row() < len(self.current_alarms)):
            return QVariant

        alarm = self.current_alarms[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == ALARM_NR:
                return QVariant(alarm.alarm_nr)
            elif column == ALARM_TEXT:
                return QVariant(alarm.text)
            elif column == ALARM_COUNTER:
                return QVariant(alarm.counter)
            elif column == ALARM_TIME_COMING:
                if alarm.time_coming is not None:
                    return QVariant(alarm.time_coming.strftime(TIME_PATTERN))
                else:
                    return QVariant()
            elif column == ALARM_TIME_GOING:
                if alarm.time_going is not None:
                    return QVariant(alarm.time_going.strftime(TIME_PATTERN))
                else:
                    return QVariant()
        elif role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
        elif role == Qt.TextColorRole:
            if alarm.is_acknowledged:
                return QVariant(QColor(Qt.darkGreen))
            elif alarm.is_active:
                return QVariant(QColor(Qt.red))

    def headerData(
        self, section: int, orientation: int, role: int = Qt.DisplayRole
    ) -> Any:
        """Return header data."""
        if role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == ALARM_NR:
                    return "id"
                elif section == ALARM_TEXT:
                    return "message"
                elif section == ALARM_COUNTER:
                    return "counter"
                elif section == ALARM_TIME_COMING:
                    return "time coming"
                elif section == ALARM_TIME_GOING:
                    return "time going"
                else:
                    return QVariant()
            else:
                return QVariant(section + 1)
        return QVariant()

    def rowCount(self, index: QModelIndex = QModelIndex()) -> int:
        """Return row count."""
        return len(self.current_alarms)
