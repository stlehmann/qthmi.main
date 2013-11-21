=====
Usage
=====

Features
========
* a linking interface to provide GUI objects with PLC data and vice versa
* a number of GUI classes like LineEdit, DoubleSpinBox, ComboBox, Label for 
  hooking up to PLC data 
* Numeric keyboard for input on Touch Screens
* Alarmserver
* Realtime plotting of PLC data


Connecting to a PLC
===================
Connection to a PLC is managed by a class that implements the *AbstractPLCConnector*
interface. This means implementing the following functions:

* *add_tag*
* *remove_tag*
* *write_to_plc*
* *read_from_plc*
* *poll*
* *start_autopoll*
* *stop_autopoll*

and a *cycletime* property.
Currently there is a Connector class available for *Beckhoffs TwinCAT ADS*, which we use
in this tutorial. But hopefully some more communication protocols like
*Modbus TCP* will be implemented soon.
For testing purposes it is also possible to implement Connectors with no connection
to a PLC but with a Ringbuffer and random values.

Create an instance of a specific Connector class, in this example *ADSConnector*::

    >>> from qthmi.ads.connector import ADSConnector

    >>> connector = ADSConnector()

With a connector object in place we can now add Tags. Tags connect the PLC objects
with the GUI controls in our Python project::

    >>> from qthmi.main.tag import Tag
    >>> from qthmi.ads.constants import PLCTYPE_REAL

    >>> temp_tag = Tag("temperature", 100, PLCTYPE_REAL, float)
    >>> connector.add_tag(temp_tag)

``temp_tag`` points to address number 100 on the PLC memory. The PLC-internal
datatype is ``REAL`` and it is used as a ``float`` value on the Python side.


Bind Widgets to Tags
====================
To display data we use HMIWidgets. For example we can use a HMIDoubleSpinBox to
display the data of ``temp_tag``::

    >>> import sys
    >>> from PyQt4.QtGui import *
    >>> from PyQt4.QtCore import *
    >>> from qthmi.ads.connector import ADSConnector
    >>> from qthmi.main.tag import Tag
    >>> from qthmi.main.widgets import HMIDoubleSpinBox

    >>> class MyWidget(QWidget):
    ...     def __init__(self, parent=None):
    ...         super(MyWidget, self).__init__(parent)
    ...
    ...         self.connector = ADSConnector()
    ...         self.connector.add_tag(Tag("temperature", 100, PLCTYPE_REAL, float))
    ...         self.temperature_spinbox = HMIDoubleSpinBox(
    ...             self.connector.tags["temperature"])
    ...
    ...         self.setLayout(QVBoxLayout())
    ...         self.layout().addWidget(self.temperature_spinbox
    ...
    ...         self.connector.start_autopoll(200)

    >>> if __name__ == "__main__":
    ...     app = QApplication(sys.argv)
    ...     f = MyWidget()
    ...     f.show()
    ...     app.exec_()

This example binds the HMIDoubleSpinBox to the *temperature* Tag and places it
into a QWidget. Autopolling is started by the ``start_autpoll`` function. The
argument passes the interval time in ms.