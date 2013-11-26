"""
Realtime data plotting
======================

Plot PLC data in Realtime.

For HMIPlot to work we need the following packages::

    >>> import sys
    >>> from PyQt4.QtGui import QApplication
    >>> from qthmi.main.connector import AbstractPLCConnector
    >>> from qthmi.main.tag import Tag
    >>> app = QApplication(sys.argv)

Now we create a new Connector and the HMIPlot object::

    >>> connector = AbstractPLCConnector()
    >>> plot = HMIPlot(connector)
    >>> type(plot)
    <class 'qthmi.main.plot.HMIPlot'>

The C{add_observer()} method is used to creat an Observer object collecting
data from the given Tag::

    >>> tag1 = connector.add_tag(Tag("tag1", 0))
    >>> plot.add_observer(tag1, "Tag1", ax=0, style="b-")
    >>> type(plot.observers[0])
    <class 'qthmi.main.plot.Observer'>

The HMIPlot object is inherited from C{QWidget} and can be displayed on its own
by calling the C{show()} function or embedded in a second QWidget object.

"""
__author__ = "Stefan Lehmann"


import datetime
import pylab
from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from qthmi.main.widgets import HMIWidget


class Observer(HMIWidget):
    """
    Binding object between a Tag and HMIPlot

    """

    def __init__(self, tag, buffer_size=100, label="", ax=0, style="-"):
        super(Observer, self).__init__()
        self.buffer_size = buffer_size
        self.y = []
        self.x = []
        self.tag = tag
        self.label = tag.name if label == "" else label
        self.ax = ax
        self.style = style

    def read_value_from_tag(self):
        self.x.append(datetime.datetime.now())
        self.y.append(self.tag.value)

        if len(self.x) > self.buffer_size:
            self.x = self.x[-self.buffer_size:]
            self.y = self.y[-self.buffer_size:]

    def write_value_to_tag(self):
        pass


class HMIPlot (QWidget, object):
    """
    Realtime Plot

    @type connector: connector.PLCConnector
    @ivar connector: connector instance for plc communication
    """

    def __init__(self, connector, parent=None, buffer_size=100, autorefresh=True):
        """
        @type connector: qthmi.main.connector.AbstractPLCConnector

        """
        super(HMIPlot, self).__init__(parent)
        self.connector = connector
        self.buffer_size = buffer_size
        self.observers = []
        self.lines = []

        #Init matplotlib objects
        #----------------------------------------------------
        self.fig = pylab.figure(1)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.axes = [self.fig.add_subplot(111)]
        self.axes.append(self.axes[0].twinx())

        #Layout
        #----------------------------------------------------
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.canvas)

        if autorefresh:
            self.connect(self.connector, SIGNAL("polled()"), self.refresh)

    def add_observer(self, tag, label="", ax=0, style="-"):
        """
        Add observer to HMIPlot.
        @type observer: Observer

        """
        observer = Observer(tag, self.buffer_size, label, ax, style)
        self.observers.append(observer)

        self.lines.append(
            self.axes[ax].plot([], [], observer.style, label=observer.label)[0])

    def refresh(self):
        """
        Plot current data.

        """
        self.axes[0].set_xlim(
            datetime.datetime.now() - datetime.timedelta(
                milliseconds=self.buffer_size * self.connector.cycletime),
            datetime.datetime.now()
        )

        for i, observer in enumerate(self.observers):
            observer.read_value_from_tag()
            self.lines[i].set_data(observer.x, observer.y)
            self.canvas.draw()
