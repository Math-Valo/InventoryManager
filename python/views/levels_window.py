from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QAbstractItemView,
                             QHeaderView, QLabel, QPushButton, QTableWidgetItem, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import math


class LevelsWindow(QWidget):
    def __init__(self, df_store_profile, results_phase_1) -> None:
        super().__init__()
        self.df_store = df_store_profile
        self.minimum_capacity_percentage = results_phase_1.minimum_capacity_percentage
        self.maximum_capacity_percentage = results_phase_1.maximum_capacity_percentage
        self.minimum_acceptable_coverage = results_phase_1.minimum_acceptable_coverage
        self.maximum_acceptable_coverage = results_phase_1.maximum_acceptable_coverage

        # Inicialización de atributos propios de la ventana (buenas prácticas)
        self.table = None
        self.sum_expected_level = None
        self.continue_button = None

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Niveles calculados")
        # self.setGeometry(100, 100, 1600, 800)
        self.resize(1200, 800)

        # Layout principal
        layout = QVBoxLayout()

        # Crear la tabla para los datos
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["Tienda", "Stock mínimo", "Capacidad ideal", "Stock máximo",
                                              "Movimiento", "Inventario final", "Nivelado final", "Cobertura"])
        self.table.setRowCount(len(self.df_store))

        # Hacer que la tabla permita el scrolling
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)

        layout.addWidget(self.table)

        # Agregar etiqueta que indica el fuera de nivel
        layout_total_level = QHBoxLayout()
        self.sum_expected_level = QLabel(f"Fuera de tienda = {self.df_store['ExpectedLevel'].sum()}")
        self.set_total_levels_color(self.df_store['ExpectedLevel'].sum())
        layout_total_level.addWidget(self.sum_expected_level, alignment=Qt.AlignCenter)
        layout.addLayout(layout_total_level)

        # Agregar botón "Siguiente >>>"
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.continue_button = QPushButton("Siguiente >>>")
        button_layout.addWidget(self.continue_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Agregar los datos a la tabla 
        self.populate_table()

    def populate_table(self):
        for row, item in self.df_store.iterrows():
            store_item = QTableWidgetItem(f"{item['CodAlmacen']} - {item['ShortName']}")
            store_item.setFlags(Qt.ItemIsEnabled)  # No editable
            self.table.setItem(row, 0, store_item)

            minimum_capacity = math.ceil(item["Capacidad"]*self.minimum_capacity_percentage)
            capacity_item = QTableWidgetItem(str(minimum_capacity))
            capacity_item.setFlags(Qt.ItemIsEnabled)  # No editable
            self.table.setItem(row, 1, capacity_item)

            capacity_item = QTableWidgetItem(str(item["Capacidad"]))
            capacity_item.setFlags(Qt.ItemIsEnabled)  # No editable
            self.table.setItem(row, 2, capacity_item)

            maximum_capacity = math.floor(item["Capacidad"]*self.maximum_capacity_percentage)
            capacity_item = QTableWidgetItem(str(maximum_capacity))
            capacity_item.setFlags(Qt.ItemIsEnabled)  # No editable
            self.table.setItem(row, 3, capacity_item)

            # spinbox para modificar el valor del movimiento esperado
            spinbox_level = QSpinBox()
            spinbox_level.setMinimum(-99999)  # Valor mínimo del nivel final = -99999
            spinbox_level.setMaximum(99999)  # Valor máximo del nivel final = 99999
            spinbox_level.setValue(item["ExpectedLevel"])
            self.table.setCellWidget(row, 4, spinbox_level)

            stock_item = QTableWidgetItem(str(item["Stock"] + item["ExpectedLevel"]))
            stock_item.setFlags(Qt.ItemIsEnabled)  # No editable
            self.set_stock_color(stock_item, item["Capacidad"], item["Stock"], item["ExpectedLevel"])
            self.table.setItem(row, 5, stock_item)

            fashion_stock_item = QTableWidgetItem(str(item["CurrentInventory"] + item["ExpectedLevel"]))
            fashion_stock_item.setFlags(Qt.ItemIsEnabled)  # No editable
            self.set_fashion_stock_color(fashion_stock_item, item["CurrentInventory"], item["ExpectedLevel"])
            self.table.setItem(row, 6, fashion_stock_item)

            if item["AvgMonthlySalesLastQuarter"] != 0:
                new_coverage = (item["CurrentInventory"]+item["ExpectedLevel"])/item["AvgMonthlySalesLastQuarter"]
            else: 
                new_coverage = -1
            coverage_item = QTableWidgetItem(str(new_coverage))
            coverage_item.setFlags(Qt.ItemIsEnabled)  # No editable
            self.set_coverage_color(coverage_item,
                                    item["CurrentInventory"],
                                    item["AvgMonthlySalesLastQuarter"],
                                    item["ExpectedLevel"])
            self.table.setItem(row, 7, coverage_item)

    def set_stock_color(self, item, capacity, stock, level):
        # Cambiar color de la etiqueta del stock a rojo si es mayor a la capacidad de la tienda
        discriminant1 = stock + level < capacity*self.minimum_capacity_percentage
        discriminant2 = stock + level > capacity*self.maximum_capacity_percentage
        if discriminant1 or discriminant2:
            item.setForeground(QColor('red'))
        elif stock + level > capacity:
            item.setForeground(QColor('orange'))
        else:
            item.setForeground(QColor('black'))

    @staticmethod
    def set_fashion_stock_color(item, fashion_stock, level):
        # Cambiar color de la etiqueta del inventario de modas a rojo si es menor a 0
        if fashion_stock + level < 0:
            item.setForeground(QColor('red'))
        else:
            item.setForeground(QColor('black'))

    def set_coverage_color(self, item, coverage, average_sales, level):
        if average_sales != 0:
            new_coverage = (coverage + level)/average_sales
        else: 
            new_coverage = -1
        if new_coverage < self.minimum_acceptable_coverage or new_coverage > self.maximum_acceptable_coverage:
            item.setForeground(QColor('red'))
        else:
            item.setForeground(QColor('black'))

    def set_total_levels_color(self, total_levels):
        if total_levels != 0:
            self.sum_expected_level.setStyleSheet("color: red")
        else:
            self.sum_expected_level.setStyleSheet("color: black")


if __name__ == "__main__":
    import pandas as pd
    from PyQt5.QtWidgets import QApplication

    class Test:
        def __init__(self) -> None:
            self.store_profile = \
                pd.DataFrame({"CodAlmacen": ["007", "008", "014"],
                              "ShortName": ["Plaza Galerías", "Plaza La Isla", "ASUR T2"],
                              "Capacidad": [1400, 1300, 1200],
                              "Stock": [1372, 1440, 891],
                              "ExpectedLevel": [-51, -49, 100],
                              "CurrentInventory": [21, 34, 10],
                              "Coverage": [1.0, 3.2, 4.5],
                              "AvgMonthlySalesLastQuarter": [4, 1, 10]})
            self.minimum_acceptable_coverage = 2.5
            self.maximum_acceptable_coverage = 4
            # Límites respecto al porcentaje de la capacidad de la tienda
            self.minimum_capacity_percentage = 0.8
            self.maximum_capacity_percentage = 1.2
            # Límite de prendas que se puede poner o quitar en una tienda
            self.maximum_movement_to_add = 100
            self.maximum_movement_to_remove = -100
            # Límites inferior y superior para el rango del nivel respecto al esperado
            self.range_lower_limite = -50
            self.range_upper_limite = 50

    app = QApplication([])
    resultados = Test()
    # view = LevelsWindow(resultados)
    # view.show()
    exit(app.exec_())
