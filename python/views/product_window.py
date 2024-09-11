from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableView, QHeaderView, QApplication)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel


class ProductWindow(QWidget):
    def __init__(self, df_product, headers=None) -> None:
        super().__init__()
        self.df_product = df_product
        self.headers = headers

        # Inicialización de atributos propios de la ventana (buenas prácticas)
        self.search_box = None
        self.search_button = None
        self.table_view = None
        self.continue_button = None
        self.model = None

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Productos por nivelar")
        self.resize(1300, 600)

        # Layout principal
        main_layout = QVBoxLayout()

        # Vista de búsqueda:
        # Layout horizontal con la etiqueta, cuadro de texto y botón de búsqueda
        search_layout = QHBoxLayout()
        search_label = QLabel("Consulta:")
        self.search_box = QLineEdit()
        query_ejemplo = "\"(Agrupador == 'P-V 24' | Agrupador == 'O-I 24') & Costo > 200\""
        self.search_box.setPlaceholderText("Ingrese query (ejemplo: " + query_ejemplo + ")")
        self.search_button = QPushButton("Buscar")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_button)
        main_layout.addLayout(search_layout)

        # Vista de la tabla
        self.table_view = QTableView()
        main_layout.addWidget(self.table_view)

        # Modelo de datos
        self.model = QStandardItemModel()
        self.update_selected_products(self.df_product)

        # Modelo Proxy para filtrar
        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(self.model)
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.table_view.setModel(proxy_model)
        # Ajuste del tamaño de columnas
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Botón para cargar la tabla a la salida y continuar a la siguiente ventana
        self.continue_button = QPushButton("Continuar >>>")
        self.continue_button.setIconSize(QSize(16, 16))
        self.continue_button.setCheckable(False)
        main_layout.addWidget(self.continue_button)

        self.setLayout(main_layout)

    def update_selected_products(self, df_product):
        self.model.setHorizontalHeaderLabels(df_product[self.headers].columns)
        for row in df_product[self.headers].itertuples(index=False):
            items = [QStandardItem(str(item)) for item in row]
            self.model.appendRow(items)


if __name__ == "__main__":
    import sys
    import pandas as pd
    app = QApplication(sys.argv)

    # DataFrame de muestra
    data = {
        "SKU": ["001", "002", "003", "004"],
        "Descripcion": ["Camisa", "Pantalones", "Falda", "Chaqueta"],
        "Agrupador": ["A1", "A2", "A1", "A2"],
        "Color": ["Rojo", "Azul", "Verde", "Negro"],
        "Talla": ["M", "L", "S", "XL"],
        "Modelo": ["Mod1", "Mod2", "Mod3", "Mod4"],
        "Marca": ["Marca1", "Marca2", "Marca1", "Marca2"],
        "Costo": [10.0, 20.0, 15.0, 25.0]
    }
    df = pd.DataFrame(data)

    # Crear y mostrar la ventana de selección de productos
    main_window = ProductWindow(df)
    main_window.show()

    sys.exit(app.exec_())
