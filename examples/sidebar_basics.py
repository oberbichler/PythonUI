import python_ui as ui


class Window(ui.ApplicationWindow):
    def __init__(self):
        super(Window, self).__init__(
            title='Example',
        )

        # Declare some options to store the user input

        self.textbox_value = ui.Option(
            value='',
            action=lambda value: print(f'You typed "{value}" into the Textbox')
        )

        self.spinbox_value = ui.Option(
            value=0,
            action=lambda value: print(f'You set "{value}" with the Spinbox')
        )

        self.checkbox_value = ui.Option(
            value=False,
            action=lambda value: print(f'You set the checkbox to "{value}"')
        )

        self.combobox_value = ui.Option(
            value=0,
            action=lambda value: print(f'You choosed "{value}" with' +
                                       ' the Combobox')
        )

        self.radiobuttons_value = ui.Option(
            value=0,
            action=lambda value: print(f'You choosed "{value}" with' +
                                       ' the Radiobuttons')
        )

    def _build_sidebar(self, builder):
        # Add some controls to the sidebar

        builder.add_label(
            label='This is a Label',
        )

        builder.add_button(
            label='This is a Button',
            action=lambda: print('You clicked on the button!'),
        )

        builder.add_textbox(
            label='This is a Textbox...',
            prefix='...with a prefix...',
            postfix='...and a postfix',
            option=builder.context.textbox_value,
        )

        builder.add_space()  # just add some space between two controls

        builder.add_spinbox(
            label='This is a Spinbox...',
            prefix='...with a prefix...',
            postfix='...and a postfix',
            option=builder.context.spinbox_value,
        )

        builder.add_checkbox(
            label='This is a Checkbox',
            option=builder.context.checkbox_value,
        )

        builder.add_combobox(
            items=[
                'Item 1',
                'Item 2',
            ],
            option=builder.context.combobox_value,
        )

        builder.add_radiobuttons(
            items=[
                'Item 1',
                'Item 2',
            ],
            option=builder.context.radiobuttons_value,
        )

        builder.add_stretch()


Window.run()
