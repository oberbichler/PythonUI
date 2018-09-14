from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
import inspect
import sys


class Option(QtCore.QObject):
    _changed = QtCore.pyqtSignal(object)

    def __init__(self, value, action=None):
        super(Option, self).__init__()
        self.value = value

        if action:
            self.connect(action)

    def connect(self, action):
        self._changed.connect(action)

    def change(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._changed.emit(value)


class Stream(QtCore.QObject):
    text_written = QtCore.pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))


class Console(QtWidgets.QTextEdit):
    def __init__(self):
        super(Console, self).__init__()
        font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        self.setFont(font)
        self.setReadOnly(True)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)

    def write(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()


class WidgetBuilder(object):
    def __init__(self, ground, context):
        self._ground = ground
        self.context = context

    def _add_widget(self, widget):
        self._ground.addWidget(widget)

        return widget

    def add(self, widget_type):
        widget = widget_type()
        builder = WidgetBuilder(self._ground, self.context)
        widget.build(builder)
        self._ground.addWidget(widget)

        return widget

    def add_label(self, label):
        widget = QtWidgets.QLabel(label)
        self._ground.addWidget(widget)

        return widget

    def add_button(self, label, action):
        widget = QtWidgets.QPushButton(label)
        self._ground.addWidget(widget)

        if len(inspect.signature(action).parameters) == 0:
            widget.clicked.connect(action)
        else:
            widget.clicked.connect(lambda: action(self.context))

        return widget

    def add_checkbox(self, label, option):
        widget = QtWidgets.QCheckBox(label)
        widget.setChecked(option.value)
        self._ground.addWidget(widget)

        option.connect(widget.setChecked)
        widget.clicked.connect(option.change)

        return widget

    def add_textbox(self, label, option, prefix=None, postfix=None):
        if label:
            widget = QtWidgets.QLabel(label)
            self._add_widget(widget)

        row = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row.setLayout(row_layout)
        self._ground.addWidget(row)

        if prefix:
            widget = QtWidgets.QLabel(prefix)
            row_layout.addWidget(widget)

        widget = QtWidgets.QLineEdit()
        widget.setText(option.value)

        row_layout.addWidget(widget, 1)

        if option:
            option.connect(widget.setText)
            widget.textChanged.connect(option.change)

        if postfix:
            widget = QtWidgets.QLabel(postfix)
            row_layout.addWidget(widget)

        return widget

    def add_spinbox(self, label, option, prefix=None, postfix=None,
                    dtype=float, minimum=None, maximum=None, step=None,
                    decimals=None):
        if label:
            widget = QtWidgets.QLabel(label)
            self._add_widget(widget)

        row = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row.setLayout(row_layout)
        self._ground.addWidget(row)

        if prefix:
            widget = QtWidgets.QLabel(prefix)
            row_layout.addWidget(widget)

        if dtype is int:
            widget = QtWidgets.QSpinBox()
            widget.setValue(option.value)
            widget.setMinimum(minimum or -2147483648)
            widget.setMaximum(maximum or 2147483647)
            widget.setSingleStep(step or 1)
        elif dtype is float:
            widget = QtWidgets.QDoubleSpinBox()
            widget.setValue(option.value)
            widget.setMinimum(minimum or -Qt.qInf())
            widget.setMaximum(maximum or Qt.qInf())
            widget.setSingleStep(step or 0.1)
            widget.setDecimals(decimals or 5)
        else:
            raise ValueError(f'Invalid dtype "{dtype.__name__}"')

        row_layout.addWidget(widget, 1)

        if option:
            option.connect(widget.setValue)
            widget.valueChanged.connect(option.change)

        if postfix:
            widget = QtWidgets.QLabel(postfix)
            row_layout.addWidget(widget)

        return widget

    def add_tabs(self, content=[], option=None):
        widget = TabsWidget(self.context)
        self._ground.addWidget(widget)

        for label, widget_type in content:
            widget.add_tab(label, widget_type)

        if option:
            option.connect(widget.setCurrentIndex)
            widget.currentChanged.connect(option.change)

        return widget

    def add_pages(self, items, option=None):
        widget = PagesWidget(self.context, items, option)
        self._ground.addWidget(widget)

        return widget

    def add_group(self, label, content):
        widget = QtWidgets.QGroupBox(label)
        self._ground.addWidget(widget)

        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        content_widget = content()
        content_widget._build(self.context)

        layout.addWidget(content_widget)

        return widget

    def add_combobox(self, label, items, option):
        if label:
            widget = QtWidgets.QLabel(label)
            self._add_widget(widget)

        widget = QtWidgets.QComboBox()
        self._ground.addWidget(widget)

        for item in items:
            widget.addItem(str(item))

        if option:
            option.connect(widget.setCurrentIndex)
            widget.currentIndexChanged.connect(option.change)

        return widget

    def add_space(self):
        widget = QtWidgets.QSpacerItem(16, 16)
        self._ground.addItem(widget)

        return widget

    def add_stretch(self):
        self._ground.addStretch(1)


class Widget(QtWidgets.QWidget):
    def __init__(self):
        super(Widget, self).__init__()

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self._ground = layout

    def _build(self, context):
        builder = WidgetBuilder(self._ground, context)
        self.build(builder)

    def build(self, builder):
        pass


class PagesWidget(QtWidgets.QWidget):
    def __init__(self, context, pages, option):
        super(PagesWidget, self).__init__()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        combobox = QtWidgets.QComboBox()
        layout.addWidget(combobox)
        self._combobox = combobox

        stack = QtWidgets.QStackedWidget()
        layout.addWidget(stack)
        self._stack = stack

        for label, widget_type in pages:
            content = widget_type()

            builder = WidgetBuilder(content._ground, context)
            content.build(builder)

            self._add_page(label, content)

        combobox.currentIndexChanged.connect(self._select_index)

        if option:
            combobox.currentIndexChanged.connect(option)
            option.connect(self.select_index)

        self._select_index(0)

    def _select_index(self, index):
        self._combobox.setCurrentIndex(index)

        if self._stack.currentWidget():
            self._stack.currentWidget().setSizePolicy(
                QtWidgets.QSizePolicy.Ignored,
                QtWidgets.QSizePolicy.Ignored)

        self._stack.setCurrentIndex(index)

        if self._stack.currentWidget():
            self._stack.currentWidget().setSizePolicy(
                QtWidgets.QSizePolicy.Preferred,
                QtWidgets.QSizePolicy.Preferred)

    def _add_page(self, key, widget):
        if self._stack.count() != 0:
            widget.setSizePolicy(
                QtWidgets.QSizePolicy.Ignored,
                QtWidgets.QSizePolicy.Ignored)

        self._combobox.addItem(str(key), key)

        self._stack.addWidget(widget)

        return widget


class TabsWidget(QtWidgets.QTabWidget):
    def __init__(self, context):
        super(TabsWidget, self).__init__()
        self.context = context

    def add_tab(self, label, widget_type=None):
        widget = widget_type()

        builder = WidgetBuilder(widget._ground, self.context)
        widget.build(builder)

        widget.setContentsMargins(8, 8, 8, 8)

        self.addTab(widget, label)

        return widget


class Sidebar(QtWidgets.QScrollArea):
    def __init__(self):
        super(Sidebar, self).__init__()

        widget = Widget()

        self._ground = widget._ground

        self.setWidget(widget)
        self._ground.setContentsMargins(8, 8, 8, 8)
        self.horizontalScrollBar().setEnabled(False)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setWidgetResizable(True)
        self.setMinimumWidth(400)


class PlotCanvas(QtWidgets.QWidget):
    _redraw = QtCore.pyqtSignal(object)

    def __init__(self, redraw):
        super(PlotCanvas, self).__init__()

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        figure = Figure()
        canvas = FigureCanvasQTAgg(figure)
        canvas.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(canvas, 1, 1, 1, 1)
        self._canvas = canvas

        plot = figure.add_subplot(111)
        figure.tight_layout()
        plot.set_aspect('equal')
        self._plot = plot

        self._redraw.connect(redraw)

    def redraw(self):
        plot = self._plot

        plot.clear()

        self._redraw.emit(plot)

        self._canvas.draw()


class ApplicationWindow(QtWidgets.QWidget):
    def __init__(self, title='', size=(1200, 800)):
        super(ApplicationWindow, self).__init__()

        self.resize(*size)
        self.setWindowTitle(title)

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.content = PlotCanvas(self._draw)
        self.console = Console()
        self.sidebar = Sidebar()

        vsplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        vsplitter.addWidget(self.content)
        vsplitter.addWidget(self.console)
        vsplitter.setStretchFactor(0, 1)
        vsplitter.setStretchFactor(1, 0)

        hsplitter = QtWidgets.QSplitter()
        hsplitter.addWidget(self.sidebar)
        hsplitter.addWidget(vsplitter)
        hsplitter.setStretchFactor(0, 0)
        hsplitter.setStretchFactor(1, 1)

        self.layout().addWidget(hsplitter)

    @classmethod
    def run(cls):
        app = QtWidgets.QApplication([])

        app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))

        widget = cls()
        widget._build(widget)

        widget.show()

        app.exec_()

    def show_dialog(self, widget_type, title='', size=None, modal=True):
        dialog = QtWidgets.QDialog(self, QtCore.Qt.WindowCloseButtonHint)
        dialog.setWindowTitle(title)
        dialog.setModal(modal)

        widget = widget_type()
        widget._build(self)

        if size:
            dialog.resize(*size)
        else:
            dialog.resize(widget.size())

        layout = QtWidgets.QGridLayout()
        dialog.setLayout(layout)
        layout.addWidget(widget)

        dialog.show()

    def show_openfiledialog(self, title=None, filters=None):
        filter = ';;'.join(filters) if isinstance(filters, list) else filters

        result = QtWidgets.QFileDialog.getOpenFileName(self, title,
                                                       filter=filter)

        return result

    def show_savefiledialog(self, title=None, filters=None):
        filter = ';;'.join(filters) if isinstance(filters, list) else filters

        result = QtWidgets.QFileDialog.getSaveFileName(self, title,
                                                       filter=filter)

        return result

    def showEvent(self, event):
        self._old_stdout = sys.stdout
        sys.stdout = Stream(text_written=self.__write_log)

    def hideEvent(self, event):
        sys.stdout = self._old_stdout

    def __write_log(self, text):
        cursor = self.console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()

    def _build(self, context):
        sidebar_builder = WidgetBuilder(self.sidebar._ground, context)
        self._build_sidebar(sidebar_builder)
        self.redraw()

    def _build_sidebar(self, builder):
        pass

    def redraw(self):
        self.content.redraw()

    def _draw(self, plot):
        pass
