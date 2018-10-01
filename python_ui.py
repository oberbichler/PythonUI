from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
import inspect
import sys


class UpperValidator(QtGui.QValidator):
    def __init__(self, parent=None):
        super(UpperValidator, self).__init__(parent)

    def validate(self, string, pos):
        if string.isupper():
            return QtGui.QValidator.Acceptable, string, pos
        else:
            return QtGui.QValidator.Intermediate, string, pos

    def fixup(self, string):
        return string.upper()


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

    def add(self, widget_type):
        widget = widget_type()
        builder = WidgetBuilder(self._ground, self.context)
        widget.build(builder)
        self._add_widget(widget)

    def add_space(self):
        spacer_item = QtWidgets.QSpacerItem(16, 16)
        self._ground.addItem(spacer_item)

    def add_stretch(self):
        self._ground.addStretch(1)

    def add_label(self, label):
        label_widget = QtWidgets.QLabel(label)
        self._add_widget(label_widget)

    def add_button(self, label, action):
        button_widget = QtWidgets.QPushButton(label)
        self._add_widget(button_widget)

        if len(inspect.signature(action).parameters) == 0:
            button_widget.clicked.connect(action)
        else:
            button_widget.clicked.connect(lambda: action(self.context))

    def add_textbox(self, label, option, prefix=None, postfix=None,
                    validator=None):
        if label:
            label_widget = QtWidgets.QLabel(label)
            self._add_widget(label_widget)

        row_widget = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_widget.setLayout(row_layout)
        self._add_widget(row_widget)

        if prefix:
            prefix_widget = QtWidgets.QLabel(prefix)
            row_layout.addWidget(prefix_widget)

        textbox_widget = QtWidgets.QLineEdit()
        if validator:
            textbox_widget.setValidator(validator(textbox_widget))
        textbox_widget.setText(option.value)

        row_layout.addWidget(textbox_widget, 1)

        if option:
            option.connect(textbox_widget.setText)
            textbox_widget.textChanged.connect(option.change)

        if postfix:
            postfix_widget = QtWidgets.QLabel(postfix)
            row_layout.addWidget(postfix_widget)

    def add_spinbox(self, label, option, prefix=None, postfix=None,
                    dtype=float, minimum=None, maximum=None, step=None,
                    decimals=None):
        if label:
            label_widget = QtWidgets.QLabel(label)
            self._add_widget(label_widget)

        row_widget = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_widget.setLayout(row_layout)
        self._add_widget(row_widget)

        if prefix:
            prefix_widget = QtWidgets.QLabel(prefix)
            row_layout.addWidget(prefix_widget)

        if dtype is int:
            spinbox_widget = QtWidgets.QSpinBox()
            spinbox_widget.setValue(option.value)
            spinbox_widget.setMinimum(minimum or -2147483648)
            spinbox_widget.setMaximum(maximum or 2147483647)
            spinbox_widget.setSingleStep(step or 1)
        elif dtype is float:
            spinbox_widget = QtWidgets.QDoubleSpinBox()
            spinbox_widget.setValue(option.value)
            spinbox_widget.setMinimum(minimum or -Qt.qInf())
            spinbox_widget.setMaximum(maximum or Qt.qInf())
            spinbox_widget.setSingleStep(step or 0.1)
            spinbox_widget.setDecimals(decimals or 5)
        else:
            raise ValueError(f'Invalid dtype "{dtype.__name__}"')

        spinbox_widget.setKeyboardTracking(False)
        row_layout.addWidget(spinbox_widget, 1)

        if option:
            option.connect(spinbox_widget.setValue)
            spinbox_widget.valueChanged.connect(option.change)

        if postfix:
            postfix_widget = QtWidgets.QLabel(postfix)
            row_layout.addWidget(postfix_widget)

    def add_checkbox(self, label, option):
        checkbox_widget = QtWidgets.QCheckBox(label)
        checkbox_widget.setChecked(option.value)
        self._add_widget(checkbox_widget)

        option.connect(checkbox_widget.setChecked)
        checkbox_widget.clicked.connect(option.change)

    def add_combobox(self, items, option, label=None):
        if label:
            label_widget = QtWidgets.QLabel(label)
            self._add_widget(label_widget)

        combobox_widget = QtWidgets.QComboBox()
        self._add_widget(combobox_widget)

        for item in items:
            combobox_widget.addItem(str(item))

        if option:
            option.connect(combobox_widget.setCurrentIndex)
            combobox_widget.currentIndexChanged.connect(option.change)

    def add_radiobuttons(self, items, option):
        button_group = QtWidgets.QButtonGroup(self._ground.parent())

        for i, item in enumerate(items):
            radio_button = QtWidgets.QRadioButton(item)
            button_group.addButton(radio_button, i)
            self._add_widget(radio_button)

        def toggled(button, checked):
            if not checked:
                return
            button_id = button_group.id(button)
            option.change(button_id)

        def toggle(button_id):
            button = button_group.button(button_id)
            button.toggle()

        if option:
            toggle(option.value)
            button_group.buttonToggled.connect(toggled)
            option.connect(toggle)

    def add_group(self, label, content):
        group_widget = QtWidgets.QGroupBox(label)
        self._add_widget(group_widget)

        group_layout = QtWidgets.QVBoxLayout()
        group_widget.setLayout(group_layout)

        content_widget = content()
        content_widget._build(self.context)

        group_layout.addWidget(content_widget)

    def add_tabs(self, items, option=None):
        tabs_widget = TabsWidget(self.context)
        self._add_widget(tabs_widget)

        for label, widget_type in items:
            tabs_widget.add_tab(label, widget_type)

        if option:
            option.connect(tabs_widget.setCurrentIndex)
            tabs_widget.currentChanged.connect(option.change)

    def add_stack(self, items, option=None):
        stack_widget = StackWidget(self.context, items, option)
        self._add_widget(stack_widget)

    def add_pages(self, items, option=None):
        pages_widget = PagesWidget(self.context, items, option)
        self._add_widget(pages_widget)


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


class StackWidget(QtWidgets.QWidget):
    def __init__(self, context, items, option):
        super(StackWidget, self).__init__()

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        stack = QtWidgets.QStackedWidget()
        layout.addWidget(stack)
        self._stack = stack

        for widget_type in items:
            widget = widget_type()

            builder = WidgetBuilder(widget._ground, context)
            widget.build(builder)

            if stack.count() != 0:
                widget.setSizePolicy(QtWidgets.QSizePolicy.Ignored,
                                     QtWidgets.QSizePolicy.Ignored)

            stack.addWidget(widget)

        if option:
            option.connect(self._select_index)

        self._select_index(0)

    def _select_index(self, index):
        if self._stack.currentWidget():
            self._stack.currentWidget().setSizePolicy(
                QtWidgets.QSizePolicy.Ignored,
                QtWidgets.QSizePolicy.Ignored)

        self._stack.setCurrentIndex(index)

        if self._stack.currentWidget():
            self._stack.currentWidget().setSizePolicy(
                QtWidgets.QSizePolicy.Preferred,
                QtWidgets.QSizePolicy.Preferred)


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
            combobox.currentIndexChanged.connect(option.change)
            option.connect(self._select_index)

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
    def run(cls, *args, **kwargs):
        app = QtWidgets.QApplication([])

        app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))

        widget = cls(*args, **kwargs)
        widget._build(widget)

        widget.show()

        widget._started()

        app.exec_()

    def show_dialog(self, widget_type, title='', size=None, modal=True,
                    action=None):
        dialog = QtWidgets.QDialog(self, QtCore.Qt.Tool)
        dialog.setWindowTitle(title)
        dialog.setModal(modal)

        widget = widget_type()
        widget._build(self)

        if size:
            dialog.resize(*size)
        else:
            dialog.adjustSize()

        layout = QtWidgets.QGridLayout()
        dialog.setLayout(layout)
        layout.addWidget(widget)

        def close_dialog(message=None):
            dialog.close()
            if action:
                action(message)

        self.close_dialog = close_dialog

        dialog.show()

    def show_open_file_dialog(self, title=None, filters=None):
        filter = ';;'.join(filters) if isinstance(filters, list) else filters

        result = QtWidgets.QFileDialog.getOpenFileName(self, title,
                                                       filter=filter)

        return result

    def show_save_file_dialog(self, title=None, filters=None):
        filter = ';;'.join(filters) if isinstance(filters, list) else filters

        result = QtWidgets.QFileDialog.getSaveFileName(self, title,
                                                       filter=filter)

        return result

    def show_error_dialog(self, message):
        QtWidgets.QMessageBox.critical(self, 'Error', message)

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

    def _started(self):
        pass
