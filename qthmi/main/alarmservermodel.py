#-*- coding: utf-8 -*-
"""
Model for alarm handling

"""
__author__ = "Stefan Lehmann"

from PyQt4.QtGui import QColor
from PyQt4.QtCore import QAbstractTableModel, Qt, QVariant, QModelIndex, SIGNAL
from alarmserver import AlarmServer, AlarmNotDefinedError

ALARM_NR = 0
ALARM_TEXT = 1
ALARM_COUNTER = 2
ALARM_TIME_COMING = 3
ALARM_TIME_GOING = 4

COLUMN_COUNT = 5
TIME_PATTERN = "%H:%M:%S"


class AlarmServerModel(QAbstractTableModel, AlarmServer):
    """
    This class allows the user access to the alarm server via
    the model/view mechanism of the Qt framework.

    """

    def __init__(self):
        AlarmServer.__init__(self)
        super(AlarmServerModel, self).__init__()

    def _dataChanged_signal(self, alarm_nr):
        alarm = self.defined_alarms.get(alarm_nr)

        if alarm is None:
            raise AlarmNotDefinedError(alarm_nr)

        if alarm in self.current_alarms:
            row = self.current_alarms.index(alarm)
            indexTopLeft = self.index(row, 0, QModelIndex())
            indexBottomRight = self.index(row, COLUMN_COUNT - 1, QModelIndex())
            self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
                      indexTopLeft, indexBottomRight)

    def acknowledge(self, alarm_nr):
        """
        Acknowledge the current alarm with the given number
        and emit a signal 'alarm_acknowledged'

        """

        AlarmServer.acknowledge(self, alarm_nr)
        self._dataChanged_signal(alarm_nr)
        self.emit(SIGNAL("alarm_acknowledged(int)"), alarm_nr)

    def acknowledge_all(self):
        """
        Acknowledge all current alarms.

        """

        self.beginResetModel()
        for alarm in self.current_alarms:
            self.acknowledge(alarm.alarm_nr)
        self.endResetModel()

    def alarm_coming(self, alarm_nr):
        alarm = self.defined_alarms.get(alarm_nr)
        if alarm is None:
            raise AlarmNotDefinedError(alarm_nr)

        if alarm in self.current_alarms:
            AlarmServer.alarm_coming(self, alarm_nr)
            row = self.current_alarms.index(alarm)
            indexTopLeft = self.index(row, 0, QModelIndex())
            indexBottomRight = self.index(row, COLUMN_COUNT - 1, QModelIndex())

            self.emit(SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
                      indexTopLeft, indexBottomRight)
        else:
            alarm_count = len(self.current_alarms)
            self.beginInsertRows(
                QModelIndex(), alarm_count - 1, alarm_count - 1
            )
            AlarmServer.alarm_coming(self, alarm_nr)
            self.endInsertRows()

    def alarm_going(self, alarm_nr):
        AlarmServer.alarm_going(self, alarm_nr)
        self._dataChanged_signal(alarm_nr)

    def clear(self, alarm_nr):
        """
        Clear the current alarm.
        
        :param int alarm_nr: number of the alarm
        
        """
        alarm = self.defined_alarms.get(alarm_nr)
        if alarm is None:
            raise AlarmNotDefinedError(alarm_nr)

        if alarm in self.current_alarms:
            row = self.current_alarms.index(alarm)
            self.beginRemoveRows(QModelIndex(), row, row)
            AlarmServer.clear(self, alarm_nr)
            self.endRemoveRows()

    def clear_all(self):
        """
        Clear all current alarms.
        
        """
        self.beginResetModel()
        AlarmServer.clear_all(self)
        self.endResetModel()

    def columnCount(self, index=QModelIndex()):
        return COLUMN_COUNT

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or \
                not (0 <= index.row() < len(self.current_alarms)):
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
                return QVariant(alarm.time_coming.strftime(TIME_PATTERN))
            elif column == ALARM_TIME_GOING:
                time_going = alarm.time_going
                if time_going is None:
                    return QVariant()
                return QVariant(alarm.time_going.strftime(TIME_PATTERN))
        elif role == Qt.TextAlignmentRole:
            return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
        elif role == Qt.TextColorRole:
            if alarm.is_acknowledged:
                return QVariant(QColor(Qt.darkGreen))
            elif alarm.is_active:
                return QVariant(QColor(Qt.red))

    def headerData(self, section, orientation, role=Qt.DisplayRole):
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

    def rowCount(self, index=QModelIndex()):
        return len(self.current_alarms)
