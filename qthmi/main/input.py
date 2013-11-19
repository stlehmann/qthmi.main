# -*-coding: utf-8 -*-
"""
Widgets for user input via TouchScreen
"""
__author__ = "Stefan Lehmann"


from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui_numpad import Ui_numPad


DECIMAL_SEPARATOR = ","


class NumPad (QDialog, Ui_numPad):
    '''
    @summary: Nummernblock, welcher auf dem Bildschirm erscheint. Ermöglicht die Eingabe von Zahlen 
    auf einem Touchscreen
    '''
    
    def __init__(self, parent=None, text=""):
        
        super(NumPad, self).__init__(parent)
        self.setupUi(self)
        
        suffixIndex = text.indexOf(" ")
        if suffixIndex == -1:
            self.outputLineEdit.setText(text)
        else:
            self.outputLineEdit.setText(text[:suffixIndex])
            
        self.outputLineEdit.setSelection(0, self.outputLineEdit.text().length())
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
                
        self.connect(self.button0, SIGNAL("pressed()"), signalMapper, SLOT("map()"))
        self.connect(self.button1, SIGNAL("pressed()"), signalMapper, SLOT("map()"))
        self.connect(self.button2, SIGNAL("pressed()"), signalMapper, SLOT("map()"))
        self.connect(self.button3, SIGNAL("pressed()"), signalMapper, SLOT("map()"))
        self.connect(self.button4, SIGNAL("pressed()"), signalMapper, SLOT("map()"))
        self.connect(self.button5, SIGNAL("pressed()"), signalMapper, SLOT("map()"))
        self.connect(self.button6, SIGNAL("pressed()"), signalMapper, SLOT("map()"))
        self.connect(self.button7, SIGNAL("pressed()"), signalMapper, SLOT("map()"))
        self.connect(self.button8, SIGNAL("pressed()"), signalMapper, SLOT("map()"))
        self.connect(self.button9, SIGNAL("pressed()"), signalMapper, SLOT("map()"))
        self.connect(self.buttonDecimal, SIGNAL("pressed()"), signalMapper, SLOT("map()"))
        self.connect(self.buttonDel, SIGNAL("pressed()"), signalMapper, SLOT("map()"))
        
        self.connect(signalMapper, SIGNAL("mapped(QString)"), self.button_pressed)
        self.connect(self.buttonOK, SIGNAL("pressed()"), self.accept)
        self.connect(self.buttonCancel, SIGNAL("pressed()"), self.close)
        self.outputLineEdit.focusOutEvent = self.outputLineEdit_focusOutEvent
        
        doubleValidator = QDoubleValidator()
        self.outputLineEdit.setValidator(doubleValidator)
           
    def button_pressed(self, value):
    
        cursor_position = self.outputLineEdit.cursorPosition()
        
        #Bei markierten Zeichen diese löschen
        if self.outputLineEdit.selectedText().length()>0:
            cursor_position = self.outputLineEdit.selectionStart()
            self.outputLineEdit.setText(self.outputLineEdit.text().remove(self.outputLineEdit.selectionStart(), self.outputLineEdit.selectedText().length()))
        
        #Bei DEL letztes Zeichen löschen
        elif value == "DEL":
            self.outputLineEdit.setText(self.outputLineEdit.text().remove(self.outputLineEdit.cursorPosition() - 1, 1))
        
        #Wenn nicht DEL, dann Zeichen schreiben
        if value <> "DEL":
            if value == DECIMAL_SEPARATOR:
                if not DECIMAL_SEPARATOR  in self.outputLineEdit.text():
                    self.outputLineEdit.setText(self.outputLineEdit.text().insert(cursor_position, value))
            else:
                self.outputLineEdit.setText(self.outputLineEdit.text().insert(cursor_position, value))
                        
    def outputLineEdit_focusOutEvent(self, e):
        pass
