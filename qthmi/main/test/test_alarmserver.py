#-*- coding: utf-8 -*-
"""
Created on 24.09.2013
@author: lehmann
"""

import unittest
from qthmi.main.alarmserver import AlarmServer, AlarmWord, bit_value, AlarmNotDefinedError
from qthmi.main.connector import AbstractPLCConnector
from qthmi.main.tag import Tag


#####################################################
#AlarmServer
#####################################################
class AlarmServer_Test (unittest.TestCase):
    def setUp(self):
        self.server = AlarmServer()
        self.server.define_alarm(0, "alarm 1")
        self.server.define_alarm(1, "alarm 2")
        self.server.define_alarm(2, "alarm 3")

    def test_define_alarm(self):
        self.assertEqual(len(self.server.defined_alarms), 3)
        self.assertEqual(self.server.defined_alarms[0].text, "alarm 1")
        self.assertEqual(self.server.defined_alarms[1].text, "alarm 2")
        self.assertEqual(self.server.defined_alarms[2].text, "alarm 3")

    def test_raise_alarm(self):
        self.server.alarm_coming(0)
        self.assertEqual(len(self.server.current_alarms), 1)
        self.assertTrue(len(self.server.current_alarms)>0)
        self.assertTrue(self.server.unacknowledged_alarms)

    def test_acknowledge(self):
        self.server.alarm_coming(0)
        self.server.alarm_coming(1)
        self.server.acknowledge(0)

        self.assertTrue(self.server.current_alarms[0].is_acknowledged)
        self.assertFalse(self.server.current_alarms[1].is_acknowledged)
        self.assertTrue(self.server.unacknowledged_alarms)

        self.server.acknowledge(1)
        self.assertTrue(self.server.current_alarms[1].is_acknowledged)
        self.assertFalse(self.server.unacknowledged_alarms)

    def test_clear(self):
        self.server.alarm_coming(0)
        self.server.alarm_coming(1)

        self.assertEqual(len(self.server.current_alarms), 2)
        self.server.clear(0)
        self.assertEqual(len(self.server.current_alarms), 1)

    def test_clear_all(self):
        self.server.alarm_coming(0)
        self.server.alarm_coming(1)

        self.assertEqual(len(self.server.current_alarms), 2)

        self.server.clear_all()

        self.assertEqual(len(self.server.current_alarms), 0)

    def test_raise_alarm_error(self):
        self.assertRaises(Exception, self.server.alarm_coming, 4)


#####################################################
#AlarmWord
#####################################################
class TestConnector(AbstractPLCConnector):
    def __init__(self):
        super(TestConnector, self).__init__()
        self.value = 0

    def read_from_plc(self, address, datatype):
        return self.value

    def write_to_plc(self, address, value, datatype):
        pass


class MyAlarmWord(AlarmWord):
    def __init__(self, tag, alarmserver, offset):
        super(MyAlarmWord, self).__init__(tag, alarmserver, offset)

        self.alarmserver.define_alarm(0, "error 0")
        self.alarmserver.define_alarm(1, "error 1")
        self.alarmserver.define_alarm(2, "error 2")


class AlarmWord_Test(unittest.TestCase):

    def setUp(self):
        self.connector = TestConnector()
        tag = self.connector.add_tag(Tag("alarmword", 0, datatype=int))
        self.alarmserver = AlarmServer()
        self.alarmword = MyAlarmWord(tag, self.alarmserver, 0)

    def test_alarmword_value_is_0(self):
        self.connector.value = 0
        self.connector.poll()
        self.assertEqual(self.alarmword._value, 0)

    def test_alarmword_value_is_1(self):
        self.connector.value = 1
        self.connector.poll()
        self.assertEqual(self.alarmword._value, 1)

    def test_alarmserver_raises_no_alarms(self):
        self.connector.value = 0
        self.connector.poll()
        self.assertEqual(len(self.alarmserver.current_alarms), 0)

    def test_alarmserver_raises_one_alarm(self):
        self.connector.value = 1
        self.connector.poll()
        self.assertEqual(len(self.alarmserver.current_alarms), 1)

    def test_alarmserver_alarm_text(self):
        self.connector.value = 1
        self.connector.poll()
        alarm = self.alarmserver.current_alarms[0]
        self.assertEqual(alarm.text, "error 0")

    def test_alarmserver_alarm_nr(self):
        self.connector.value = 1
        self.connector.poll()
        alarm = self.alarmserver.current_alarms[0]
        self.assertEqual(alarm.alarm_nr, 0)

    def test_bit_value(self):
        word= int("0110", 2)
        self.assertEqual(bit_value(word, 0), False)
        self.assertEqual(bit_value(word, 1), True)
        self.assertEqual(bit_value(word, 2), True)
        self.assertEqual(bit_value(word, 3), False)

    def test_alarm_not_define_error(self):
        def helper_function():
            self.alarmword.value = int("1010", 2)
        self.assertRaises(AlarmNotDefinedError, helper_function)

    def test_alarm_coming_and_going(self):
        self.alarmword.value=int("10", 2)
        alarm = self.alarmserver.current_alarms[0]
        self.assertTrue(alarm.is_active)

        self.alarmword.value=int("0", 2)
        alarm = self.alarmserver.current_alarms[0]
        self.assertFalse(alarm.is_active)


if __name__ == '__main__':
   unittest.main()