# -*-coding: utf-8 -*-
"""
Widgets for user input via TouchScreen
"""
from PyQt5.QtCore import QSignalMapper
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog
from .ui_numpad import Ui_numPad
from .util import string_remove_by_index, string_insert


__author__ = "Stefan Lehmann"
DECIMAL_SEPARATOR = ","


class NumPad (QDialog, Ui_numPad):
    """
    @summary: Nummernblock, welcher auf dem Bildschirm erscheint. Ermöglicht
    die Eingabe von Zahlen auf einem Touchscreen

    """

    def __init__(self, parent=None, text=""):

        super(NumPad, self).__init__(parent)
        self.setupUi(self)

        suffixIndex = text.index(" ")
        if suffixIndex == -1:
            self.outputLineEdit.setText(text)
        else:
            self.outputLineEdit.setText(text[:suffixIndex])

        self.outputLineEdit.setSelection(0, len(self.outputLineEdit.text()))
        self.outputLineEdit.setFocus()

        self.signal_mapper = QSignalMapper(self)
        self.signal_mapper.setMapping(self.button0, "0")
        self.signal_mapper.setMapping(self.button1, "1")
        self.signal_mapper.setMapping(self.button2, "2")
        self.signal_mapper.setMapping(self.button3, "3")
        self.signal_mapper.setMapping(self.button4, "4")
        self.signal_mapper.setMapping(self.button5, "5")
        self.signal_mapper.setMapping(self.button6, "6")
        self.signal_mapper.setMapping(self.button7, "7")
        self.signal_mapper.setMapping(self.button8, "8")
        self.signal_mapper.setMapping(self.button9, "9")
        self.signal_mapper.setMapping(self.buttonDecimal, DECIMAL_SEPARATOR)
        self.signal_mapper.setMapping(self.buttonDel, "DEL")

        self.button0.pressed.connect(self.signal_mapper.map)
        self.button1.pressed.connect(self.signal_mapper.map)
        self.button2.pressed.connect(self.signal_mapper.map)
        self.button3.pressed.connect(self.signal_mapper.map)
        self.button4.pressed.connect(self.signal_mapper.map)
        self.button5.pressed.connect(self.signal_mapper.map)
        self.button6.pressed.connect(self.signal_mapper.map)
        self.button7.pressed.connect(self.signal_mapper.map)
        self.button8.pressed.connect(self.signal_mapper.map)
        self.button9.pressed.connect(self.signal_mapper.map)
        self.buttonDecimal.pressed.connect(self.signal_mapper.map)
        self.buttonDel.pressed.connect(self.signal_mapper.map)

        self.signal_mapper.mapped[str].connect(self.button_pressed)
        self.buttonOK.pressed.connect(self.accept)
        self.buttonCancel.pressed.connect(self.close)
        self.outputLineEdit.focusOutEvent = self.outputLineEdit_focusOutEvent

        doubleValidator = QDoubleValidator()
        self.outputLineEdit.setValidator(doubleValidator)

    def button_pressed(self, value):
        cursor_position = self.outputLineEdit.cursorPosition()

        # Bei markierten Zeichen diese löschen
        if len(self.outputLineEdit.selectedText()) > 0:

            cursor_position = self.outputLineEdit.selectionStart()
            selection_length = len(self.outputLineEdit.selectedText())

            self.outputLineEdit.setText(
                string_remove_by_index(
                    self.outputLineEdit.text(),
                    start_index=cursor_position,
                    length=selection_length
                )
            )

        # Bei DEL letztes Zeichen löschen
        elif value == "DEL":
            # self.outputLineEdit.setText(self.outputLineEdit.text().remove(
            #    self.outputLineEdit.cursorPosition() - 1, 1))

            self.outputLineEdit.setText(
                string_remove_by_index(
                    self.outputLineEdit.text(),
                    start_index=self.outputLineEdit.cursorPosition() - 1,
                    length=1)
            )

        # Wenn nicht DEL, dann Zeichen schreiben
        if not value == "DEL":
            if value == DECIMAL_SEPARATOR:
                if DECIMAL_SEPARATOR not in self.outputLineEdit.text():
                    self.outputLineEdit.setText(
                        string_insert(self.outputLineEdit.text(),
                                      value, cursor_position)
                    )
            else:
                self.outputLineEdit.setText(
                    string_insert(self.outputLineEdit.text(), value,
                                  cursor_position)
                )

    def outputLineEdit_focusOutEvent(self, e):
        pass
