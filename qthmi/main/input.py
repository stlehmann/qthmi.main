# -*-coding: utf-8 -*-
"""
Widgets for user input via TouchScreen
"""
from PyQt5.QtCore import QSignalMapper
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog
from .ui_numpad import Ui_numPad


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

        suffixIndex = text.indexOf(" ")
        if suffixIndex == -1:
            self.outputLineEdit.setText(text)
        else:
            self.outputLineEdit.setText(text[:suffixIndex])

        self.outputLineEdit.setSelection(
            0, self.outputLineEdit.text().length()
        )
        self.outputLineEdit.setFocus()

        signalMapper = QSignalMapper(self)
        signalMapper.setMapping(self.button0, "0")
        signalMapper.setMapping(self.button1, "1")
        signalMapper.setMapping(self.button2, "2")
        signalMapper.setMapping(self.button3, "3")
        signalMapper.setMapping(self.button4, "4")
        signalMapper.setMapping(self.button5, "5")
        signalMapper.setMapping(self.button6, "6")
        signalMapper.setMapping(self.button7, "7")
        signalMapper.setMapping(self.button8, "8")
        signalMapper.setMapping(self.button9, "9")
        signalMapper.setMapping(self.buttonDecimal, DECIMAL_SEPARATOR)
        signalMapper.setMapping(self.buttonDel, "DEL")

        self.button0.pressed.connect(signalMapper.map)
        self.button1.pressed.connect(signalMapper.map)
        self.button2.pressed.connect(signalMapper.map)
        self.button3.pressed.connect(signalMapper.map)
        self.button4.pressed.connect(signalMapper.map)
        self.button5.pressed.connect(signalMapper.map)
        self.button6.pressed.connect(signalMapper.map)
        self.button7.pressed.connect(signalMapper.map)
        self.button8.pressed.connect(signalMapper.map)
        self.button9.pressed.connect(signalMapper.map)
        self.buttonDecimal.pressed.connect(signalMapper.map)
        self.buttonDel.pressed.connect(signalMapper.map)

        self.signalMapper.mapped.connect(self.button_pressed)
        self.buttonOK.pressed.connect(self.accept)
        self.buttonCancel.pressed.connect(self.close)
        self.outputLineEdit.focusOutEvent = self.outputLineEdit_focusOutEvent

        doubleValidator = QDoubleValidator()
        self.outputLineEdit.setValidator(doubleValidator)

    def button_pressed(self, value):

        cursor_position = self.outputLineEdit.cursorPosition()

        # Bei markierten Zeichen diese löschen
        if self.outputLineEdit.selectedText().length() > 0:
            cursor_position = self.outputLineEdit.selectionStart()
            self.outputLineEdit.setText(
                self.outputLineEdit.text().remove(
                    self.outputLineEdit.selectionStart(),
                    self.outputLineEdit.selectedText().length()
                )
            )

        # Bei DEL letztes Zeichen löschen
        elif value == "DEL":
            self.outputLineEdit.setText(self.outputLineEdit.text().remove(
                self.outputLineEdit.cursorPosition() - 1, 1))

        # Wenn nicht DEL, dann Zeichen schreiben
        if not value == "DEL":
            if value == DECIMAL_SEPARATOR:
                if DECIMAL_SEPARATOR not in self.outputLineEdit.text():
                    self.outputLineEdit.setText(
                        self.outputLineEdit.text().insert(cursor_position,
                                                          value))
            else:
                self.outputLineEdit.setText(
                    self.outputLineEdit.text().insert(cursor_position, value))

    def outputLineEdit_focusOutEvent(self, e):
        pass
