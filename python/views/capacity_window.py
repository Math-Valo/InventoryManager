import sys
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, 
    QPushButton, QHBoxLayout, QAbstractItemView, QHeaderView, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class CapacityWindow(QWidget):
    def __init__(self, stores):
        super().__init__()
        self.df_store = stores

        # Inicialización de atributos propios de la ventana (buenas prácticas)
        self.table = None
        self.continue_button = None

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Modificación de capacidades")
        self.setGeometry(100, 100, 600, 800)

        # Layout principal
        layout = QVBoxLayout(self)

        # Crear la tabla para los datos
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Tienda", "Capacidad", "Ropa total"])
        self.table.setRowCount(len(self.df_store))
        
        # Hacer que la tabla permita el scrolling
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        # Agregar botón "Siguiente >>>"
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.continue_button = QPushButton("Siguiente >>>")
        button_layout.addWidget(self.continue_button)
        layout.addLayout(button_layout)

        # Agregar los datos a la tabla
        self.populate_table()

    def populate_table(self):
        for row, item in self.df_store.iterrows():
            store_item = QTableWidgetItem(f"{item['CodAlmacen']} - {item['ShortName']}")
            store_item.setFlags(Qt.ItemIsEnabled)  # No editable
            self.table.setItem(row, 0, store_item)

            # spinbox para modificar el valor de la capacidad
            spinbox = QSpinBox()
            spinbox.setMinimum(0)  # Valor mínimo de la capacidad = 0
            spinbox.setMaximum(10000)  # Valor máximo de la capacidad = 10,000
            spinbox.setValue(item["Capacidad"])
            self.table.setCellWidget(row, 1, spinbox)

            stock_item = QTableWidgetItem(str(item["Stock"]))
            stock_item.setFlags(Qt.ItemIsEnabled)  # No editable
            self.set_stock_color(stock_item, item["Capacidad"], item["Stock"])
            self.table.setItem(row, 2, stock_item)

    @staticmethod
    def set_stock_color(item, capacity, stock) -> None:
        # Cambiar color de la etiqueta del stock a rojo si es mayor a la capacidad de la tienda
        if stock > capacity:
            item.setForeground(QColor('red'))
        else:
            item.setForeground(QColor('black'))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    import pandas as pd
    df_store = pd.DataFrame({"CodAlmacen": ["007", "008", "009"],
                             "ShortName": ["FIESTA AMERICANA",
                                           "CANCUN LAS AMERICAS",
                                           "ABITO VILLAHERMOSA"],
                             "Capacidad": [1600, 1450, 1400],
                             "Stock": [1600, 1600, 1600]})

    window = CapacityWindow(df_store)
    window.show()
    sys.exit(app.exec_())
