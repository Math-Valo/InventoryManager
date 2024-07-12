from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDateEdit, QPushButton
from PyQt5.QtCore import QDate, pyqtSlot
# import datetime

class DateInventoryWindow(QWidget):
    reset_date = pyqtSlot()
    next_window = pyqtSlot()

    def __init__(self, **settings) -> None:
        super().__init__()

        self.connection = settings["database_connection"]

    def setup_ui(self):
        self.setWindowTitle("Fecha del inventario")
        self.setGeometry(100, 100, 510, 240)

        # Layout principal
        layout = QVBoxLayout()


        label = QLabel("Indique la fecha correcta de registro de inventarios:")
        layout.addWidget(label)

        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate(self.inventory_date.year,
                                self.inventory_date.month,
                                self.inventory_date.day))
        layout.addWidget(date_edit)

        # Layout para las opciones de la ventana
        layout_options = QHBoxLayout()

        # Botón para reestablecer la fecha predeterminada
        reset_date_button = QPushButton("Reestablecer predeterminada")
        reset_date_button.clicked.connect()  # Función para cambiar fecha

        # Botón para continuar a la siguiente fase de la nivelación
        continue_button = QPushButton("Continuar >>>")

        layout_options.addWidget(reset_date_button)
        layout_options.addWidget(continue_button)

        layout.addLayout(layout_options)
