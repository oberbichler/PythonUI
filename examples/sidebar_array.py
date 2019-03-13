import python_ui as ui
import numpy as np


class Window(ui.ApplicationWindow):
    def __init__(self):
        super(Window, self).__init__(
            title='Example',
        )

        self.nb_rows = ui.Option(
            value=1,
            action=self.resize_array,
        )

        self.nb_cols = ui.Option(
            value=1,
            action=self.resize_array,
        )

        self.array = ui.Option(
            value=np.eye(1),
            action=self.compute_matrix_info,
        )

        self.sum = ui.Option(
            value=1,
        )

        self.det = ui.Option(
            value=1,
        )

    def resize_array(self):
        self.array.change(np.random.rand(self.nb_rows.value,
                                         self.nb_cols.value))

    def compute_matrix_info(self):
        self.sum.change(np.sum(self.array.value))

        if self.nb_rows.value == self.nb_cols.value:
            self.det.change(np.linalg.det(self.array.value))
        else:
            self.det.change(None)

    def _build_sidebar(self, builder):
        builder.add_spinbox(
            label='Number of rows:',
            option=builder.context.nb_rows,
            dtype=int,
            minimum=1,
        )

        builder.add_spinbox(
            label='Number of cols:',
            option=builder.context.nb_cols,
            dtype=int,
            minimum=1,
        )

        builder.add_array(
            option=self.array,
            label='Editable array:',
        )

        builder.add_textbox(
            label='Sum of entries:',
            option=self.sum,
            readonly=True,
        )

        builder.add_textbox(
            label='Determinant:',
            option=self.det,
            readonly=True,
        )

        builder.add_array(
            option=self.array,
            label='Read-only array:',
            readonly=True,
        )

        builder.add_button(
            label='Copy array to clipboard',
            action=lambda: ui.copy_to_clipboard(self.array.value),
        )

        builder.add_stretch()


Window.run()
