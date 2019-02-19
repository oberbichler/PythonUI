import python_ui as ui


class Window(ui.ApplicationWindow):
    def __init__(self):
        super(Window, self).__init__(
            title='Example',
        )

        self.textbox_value = ui.Option(
            value='',
            action=lambda value: print(f'You typed "{value}" into the Textbox')
        )

    def _build_sidebar(self, builder):
        builder.add_textbox(
            label='The textbox only accepts uppercase chars (use TAB or ENTER' +
                  ' to confirm input)',
            option=builder.context.textbox_value,
            validate=lambda value: (None if any(c.isdigit() for c in value)
                                    else value.upper()),
        )

        builder.add_stretch()


Window.run()
