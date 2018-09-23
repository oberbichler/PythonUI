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
        self.letter = ui.Option(value='A')
        self.number = ui.Option(value=0)

    def _build_sidebar(self, builder):
        builder.add_button(
            label='Show dialog',
            action=lambda: self.show_dialog(Dialog,
                                            action=self.on_dialog_close),
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
            option=self.tab_index,
        )

        builder.add_space()

        builder.add_label(
            label='Label example',
        )

        builder.add_pages(
            items=[
                ('Numbers', NumberSelector),
                ('Letters and numbers', LetterAndNumberSelector),
            ],
            option=self.tab_index,
        )

        builder.add_stack(
            items=[
                NumberSelector,
                LetterAndNumberSelector,
            ],
            option=self.tab_index,
        )

        builder.add_button(
            label='Open',
            action=self.on_open_clicked,
        )

        builder.add_button(
            label='Save',
            action=self.on_save_clicked,
        )

        builder.add_button(
            label='Make some mistake',
            action=lambda: self.show_errordialog('That was wrong!'),
        )

        builder.add_radiobuttons(
            items=[
                'Option 1',
                'Option 2',
            ],
            option=self.tab_index,
        )

        builder.add_stretch()

        builder.add(Dialog)

    def _draw(self, ax):
        ax.grid()
        ax.plot([0, 1, 2], [0, self.peak.value, 0])

    def on_dialog_close(self, message):
        print(message)

    def on_open_clicked(self, args):
        result = self.show_openfiledialog(title='Open Python-File',
                                          filters='Python-Script (*.py)')

        if result is None:
            return

        filename, filetype = result

        print(f'Open "{filename}" as "{filetype}"')

    def on_save_clicked(self):
        result = self.show_savefiledialog(title='Save Python-File',
                                          filters='Python-Script (*.py)')

        if result is None:
            return

        filename, filetype = result

        print(f'Save "{filename}" as "{filetype}"')


class Dialog(ui.Widget):
    def build(self, builder):
        builder.add_button(
            label='Action',
            action=lambda: print('Action button clicked'),
        )

        builder.add_button(
            label='OK',
            action=lambda ctx: ctx.close_dialog('OK'),
        )

        builder.add_button(
            label='Cancel',
            action=lambda ctx: ctx.close_dialog('Cancel'),
        )


class SettingsA(ui.Widget):
    def build(self, builder):
        builder.add_textbox(
            label='Enter some text:',
            option=builder.context.some_text,
        )

        builder.add_button(
            label='Next',
            action=lambda: builder.context.tab_index.change(1),
        )


class SettingsB(ui.Widget):
    def build(self, builder):
        builder.add_textbox(
            label='Repeat some text:',
            option=builder.context.some_text,
        )

        builder.add_button(
            label='Back',
            action=lambda: builder.context.tab_index.change(0),
        )


class NumberSelector(ui.Widget):
    def build(self, builder):
        builder.add_combobox(
            label='Select number:',
            items=[1, 2, 3],
            option=builder.context.number,
        )


class LetterAndNumberSelector(ui.Widget):
    def build(self, builder):
        builder.add_combobox(
            label='Select letter:',
            items=['A', 'B', 'C'],
            option=builder.context.letter,
        )
        builder.add_combobox(
            label='Select number:',
            items=[1, 2, 3],
            option=builder.context.number,
        )


Window.run()
