import python_ui as ui


class Dialog(ui.Widget):
    def build(self, builder):
        builder.add_button('Close',
                           lambda ctx: ctx.close_dialog('You pushed \'Close\''))


class Window(ui.ApplicationWindow):
    def __init__(self):
        super(Window, self).__init__(
            title='Example',
        )

    def _build_sidebar(self, builder):
        builder.add_button(
            label='Open a dialog window',
            action=lambda: self.show_dialog(Dialog,
                                            title='Dialog',
                                            action=print),
        )

        builder.add_button(
            label='Make a mistake',
            action=lambda: self.show_error_dialog(
                message='Something went wrong',
            )
        )

        builder.add_button(
            label='Open a text file',
            action=lambda: print(self.show_open_file_dialog(
                extension_filters=['*.txt'],
            ))
        )

        builder.add_button(
            label='Save a text file',
            action=lambda: print(self.show_save_file_dialog(
                extension_filters=['*.txt'],
            ))
        )

        builder.add_stretch()


Window.run()
