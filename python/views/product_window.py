from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QTableView, QHeaderView, QApplication)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSize, QSortFilterProxyModel


class ProductWindow(QWidget):
    def __init__(self, df_product) -> None:
        super().__init__()
        self.df_product = df_product
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Productos por nivelar")
        self.resize(1000, 600)

        # Vista principal
        main_layout = QVBoxLayout()  # QVBoxLayout(self.centralwidget)

        # Vista de búsqueda:
        # Layout horizontal con la etiqueta, cuadro de texto y botón de búsqueda
        search_layout = QHBoxLayout()
        search_label = QLabel("Consulta:")
        search_box = QLineEdit()
        query_ejemplo = "\"(Agrupador == 'P-V 24' | Agrupador == 'P-V 24') & Costo > 200\""
        search_box.setPlaceholderText("Ingrese query (ejemplo: " + query_ejemplo + ")")
        self.search_button = QPushButton("Buscar")
        search_layout.addWidget(search_label)
        search_layout.addWidget(search_box)
        search_layout.addWidget(self.search_button)
        main_layout.addLayout(search_layout)

        # Vista de la tabla
        self.table_view = QTableView()
        main_layout.addWidget(self.table_view)

        # Modelo de datos
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(self.df_product.columns)
        for row in self.df_product.itertuples(index=False):
            items = [QStandardItem(str(item)) for item in row]
            model.appendRow(items)
        
        # Modelo Proxy para filtrar
        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.table_view.setModel(proxy_model)
        # Ajuste del tamaño de columnas
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Botón para cargar la tabla a la salida y continuar a la siguiente ventana
        self.output_button = QPushButton("Continuar >>>")
        self.output_button.setIconSize(QSize(16, 16))
        self.output_button.setCheckable(False)
        main_layout.addWidget(self.output_button)

        self.setLayout(main_layout)


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
