import python_ui as ui


class Window(ui.ApplicationWindow):
    def __init__(self):
        super(Window, self).__init__(
            title='Example',
        )

        # define options
        self.peak = ui.Option(value=2, action=lambda: self.redraw())
        self.some_text = ui.Option(value='')
        self.tab_index = ui.Option(value=0)

    def _build_sidebar(self, builder):
        builder.add_button(
            label='Show dialog',
            action=lambda: self.show_dialog(Dialog),
        )

        builder.add_spinbox(
            label='Peak',
            option=self.peak,
        )

        builder.add_tabs(
            content=[
                ('SettingsA', SettingsA),
                ('SettingsB', SettingsB),
            ],
            option=self.tab_index,
        )

        builder.add_group(
            label='Group',
            content=SettingsA,
        )

        builder.add_combobox(
            label='Select:',
            items=['A', 'B'],
            option=self.tab_index)

        builder.add_stretch()

        builder.add(Dialog)

    def _draw(self, ax):
        ax.grid()
        ax.plot([0, 1, 2], [0, self.peak.value, 0])


class Dialog(ui.Widget):
    def build(self, builder):
        builder.add_button(
            label='Action',
            action=lambda: print('Action button clicked')
        )


class SettingsA(ui.Widget):
    def build(self, builder):
        builder.add_textbox(
            label='Enter some text:',
            option=builder.context.some_text,
        )

        builder.add_button(
            label='Next',
            action=lambda: builder.context.tab_index.change(1)
        )


class SettingsB(ui.Widget):
    def build(self, builder):
        builder.add_textbox(
            label='Repeat some text:',
            option=builder.context.some_text,
        )

        builder.add_button(
            label='Back',
            action=lambda: builder.context.tab_index.change(0)
        )


Window.run()
