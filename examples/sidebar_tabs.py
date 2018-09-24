import python_ui as ui


class ContentForItem0(ui.Widget):
    def build(self, builder):
        builder.add_label(
            label='This is the content of Item 0',
        )


class ContentForItem1(ui.Widget):
    def build(self, builder):
        builder.add_label(
            label='This is the content of Item 1',
        )


class Window(ui.ApplicationWindow):
    def __init__(self):
        super(Window, self).__init__(
            title='Example',
        )

        self.selected_item = ui.Option(
            value=0,
            action=lambda value: print(f'You have selected item "{value}"')
        )

    def _build_sidebar(self, builder):
        builder.add_tabs(
            items=[
                ('Item 0', ContentForItem0),
                ('Item 1', ContentForItem1),
            ],
            option=self.selected_item,
        )

        builder.add_stretch()


Window.run()
