import python_ui as ui

class Plot(ui.PlotCanvas):
    def plot(self, ax):
        ax.text(
            x=0.5,
            y=0.5,
            s='Here is the plot canvas',
            horizontalalignment='center',
            verticalalignment='center',
        )

class Window(ui.ApplicationWindow):
    def __init__(self):
        super(Window, self).__init__(
            title='Example',
            content=Plot,
        )
        self.content.redraw()

    def _build_sidebar(self, builder):
        builder.add_label(
            label='Here is the sidebar',
        )

    def _started(self):
        print('Here is the console')


Window.run()
