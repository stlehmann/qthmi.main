"""Realtime data plotting.

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
from typing import List, Optional
from datetime import datetime, timedelta
import pylab
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.lines import Line2D
from .connector import AbstractPLCConnector
from .widgets import HMIWidget
from .tag import Tag


__author__ = "Stefan Lehmann"


class BaseObserver(HMIWidget):
    """Base Observer class."""

    def __init__(
        self,
        tag: Tag,
        buffer_size: int = 100,
        label: str = "",
        ax: int = 0,
        plot_style: str = "-",
    ) -> None:
        super().__init__(tag)
        self.buffer_size = buffer_size
        self.tag = tag
        self.label = tag.name if label == "" else label
        self.ax = ax
        self.plot_style = plot_style
        self.starttime: Optional[datetime] = None


class Observer(BaseObserver):
    """Binding object between a Tag and HMIPlot."""

    def __init__(
        self,
        tag: Tag,
        buffer_size: int = 100,
        label: str = "",
        ax: int = 0,
        plot_style: str = "-",
    ) -> None:
        super().__init__(tag)
        self.x_vals: List[datetime] = []
        self.y_vals: List[float] = []

    def read_value_from_tag(self) -> None:
        """Read value from tag."""
        self.x_vals.append(datetime.now())
        self.y_vals.append(self.tag.value)

        if len(self.x_vals) > self.buffer_size:
            self.x_vals = self.x_vals[-self.buffer_size:]
            self.y_vals = self.y_vals[-self.buffer_size:]


class TimeDeltaObserver(BaseObserver):
    """Observer for time differences."""

    def __init__(
        self,
        tag: Tag,
        buffer_size: int = 100,
        label: str = "",
        ax: int = 0,
        plot_style: str = "-",
    ) -> None:
        super().__init__(tag)
        self.x_vals: List[float] = []
        self.y_vals: List[float] = []

    def read_value_from_tag(self) -> None:
        """Read value from tag."""
        if len(self.x_vals) == 0:
            self.starttime = datetime.now()

        if self.starttime is not None:
            delta = datetime.now() - self.starttime
        else:
            delta = timedelta(0)

        self.x_vals.append(delta.total_seconds())
        self.y_vals.append(self.tag.value)

        if len(self.x_vals) > self.buffer_size:
            self.x_vals = self.x_vals[-self.buffer_size:]
            self.y_vals = self.y_vals[-self.buffer_size:]


class HMIPlot(QWidget, object):
    """Realtime Plot.

    :ivar connector: connector instance for plc communication
    """

    def __init__(
        self,
        connector: AbstractPLCConnector,
        parent: QWidget = None,
        buffer_size: int = 100,
    ) -> None:
        super(HMIPlot, self).__init__(parent)
        self.connector = connector
        self.buffer_size = buffer_size
        self.observers: List[Observer] = []
        self.lines: List[Line2D] = []

        # Init matplotlib objects
        # ----------------------------------------------------
        self.fig = pylab.figure(1)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.axes = [self.fig.add_subplot(111)]
        self.axes.append(self.axes[0].twinx())

        # Layout
        # ----------------------------------------------------
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.canvas)

        self.connector.polled.connect(self.refresh)

    def add_observer(self, observer: Observer) -> None:
        """Add observer to HMIPlot."""
        self.observers.append(observer)

        self.lines.append(
            self.axes[observer.ax].plot([], [], observer.style, label=observer.label)[0]
        )

    def autoscale_xaxis(self) -> None:
        """Autoscale x axis."""
        self.axes[0].set_xlim(
            datetime.now()
            - timedelta(milliseconds=self.buffer_size * self.connector.cycletime),
            datetime.now(),
        )

    def refresh(self) -> None:
        """Plot current data."""
        prim_observer = self.observers[0]
        if len(prim_observer.x_list) > 1:
            self.axes[0].set_xlim(prim_observer.x_list[0], prim_observer.x_list[-1])

        for i, observer in enumerate(self.observers):
            observer.read_value_from_tag()
            self.lines[i].set_data(observer.x_list, observer.y_list)
        self.draw()

    def draw(self) -> None:
        """Draw the canvas."""
        self.canvas.draw()
