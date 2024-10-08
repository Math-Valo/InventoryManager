from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDateEdit, QPushButton
from PyQt5.QtCore import QDate


class DateInventoryWindow(QWidget):
    def __init__(self, last_date_in_inventory) -> None:
        super().__init__()
        self.inventory_date = last_date_in_inventory

        # Inicialización de atributos propios de la ventana (buenas prácticas)
        self.date_edit = None
        self.reset_date_button = None
        self.continue_button = None

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Fecha del inventario")
        self.setGeometry(100, 100, 410, 140)

        # Layout principal
        layout = QVBoxLayout()

        label = QLabel("Indique la fecha de la última captura de datos de los inventarios:")
        layout.addWidget(label)

        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate(self.inventory_date.year,
                                     self.inventory_date.month,
                                     self.inventory_date.day))
        layout.addWidget(self.date_edit)

        # Layout para las opciones de la ventana
        layout_options = QHBoxLayout()

        # Botón para reestablecer la fecha predeterminada
        self.reset_date_button = QPushButton("Restablecer fecha")

        # Botón para continuar a la siguiente fase de la nivelación
        self.continue_button = QPushButton("Continuar >>>")

        layout_options.addWidget(self.reset_date_button)
        layout_options.addWidget(self.continue_button)

        layout.addLayout(layout_options)

        self.setLayout(layout)

    def set_date(self, date) -> None:
        if date is not None:
            self.date_edit.setDate(QDate(date.year, date.month, date.day))
        self.date_edit.setDate(QDate.currentDate())
