import python_ui as ui


class ContentOfTheGroup(ui.Widget):
    def build(self, builder):
        builder.add_label(
            label='This is the content of the group',
        )


class Window(ui.ApplicationWindow):
    def __init__(self):
        super(Window, self).__init__(
            title='Example',
        )

    def _build_sidebar(self, builder):
        builder.add_group(
            label='This is a Group',
            content=ContentOfTheGroup,
        )

        builder.add_stretch()


Window.run()
