from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
                             QScrollArea, QCheckBox, QTableView, QHeaderView, QSplitter)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

class StoreWindow(QWidget):
    def __init__(self, df_store) -> None:
        super().__init__()
        self.df_store = df_store

        self.regions = dict()
        self.stores = dict()

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Tiendas a nivelar")
        self.setGeometry(100, 100, 1600, 800)

        # Layout principal
        layout = QVBoxLayout()

        # Para permitir redimensionar las dos secciones del proceso
        splitter = QSplitter(Qt.Horizontal)

        # Layout para seleccionar tiendas y para mostrar tiendas seleccionadas
        selection_layout = QVBoxLayout()
        selected_section_layout = QVBoxLayout()

        # Widgets para acomodar las layout y redimensionar del lado izquierdo y derecho
        selection_widget = QWidget()
        selected_widget = QWidget()

        # Espacio de scrolling que se llenará de checkbox para seleccionar las regiones
        region_scroll_area = QScrollArea()
        region_widget = QWidget()
        region_layout = QVBoxLayout()
        region_widget.setLayout(region_layout)
        region_scroll_area.setWidget(region_widget)
        region_scroll_area.setWidgetResizable(True)

        # Espacio de scrolling que se llenará de checkbox para seleccionar las tiendas
        store_scroll_area = QScrollArea()
        store_widget = QWidget()
        store_layout = QVBoxLayout()
        store_widget.setLayout(store_layout)
        store_scroll_area.setWidget(store_widget)
        store_scroll_area.setWidgetResizable(True)

        # Espacio que se llenará con las tiendas ya seleccionadas
        selected_stores_view = QTableView()
        self.selected_stores_model = QStandardItemModel()
        selected_stores_view.setModel(self.selected_stores_model)

        # Configurar la tabla de tiendas seleccionadas
        selected_stores_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # selected_stores_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Creando checkboxes de las regiones
        regions = self.df_store["Region"].unique()
        for region in regions:
            region_checkbox = QCheckBox(region)
            region_layout.addWidget(region_checkbox)
            self.regions[region] = region_checkbox

        # Creando checkboxes de las tiendas
        for _, row in self.df_store.iterrows():
            store_checkbox = QCheckBox(f"{row['CodAlmacen']} - {row['NombreAlmacen']}")
            store_layout.addWidget(store_checkbox)
            self.stores[row["CodAlmacen"]] = store_checkbox

        # Botón para terminar selección
        self.continue_button = QPushButton("Continuar >>>")

        # Llenado de layouts
        selection_layout.addWidget(region_scroll_area)
        selection_layout.addWidget(store_scroll_area)

        selection_widget.setLayout(selection_layout)
        splitter.addWidget(selection_widget)

        selected_section_layout.addWidget(QLabel("Tiendas seleccionadas:"))
        selected_section_layout.addWidget(selected_stores_view)

        selected_widget.setLayout(selected_section_layout)
        splitter.addWidget(selected_widget)

        splitter.setStretchFactor(0,1)
        splitter.setStretchFactor(1,3)

        layout.addWidget(splitter)
        layout.addWidget(self.continue_button)

        self.setLayout(layout)

    def update_selected_stores(self, df_selected_stores):
        headers = df_selected_stores.columns.tolist()
        rename_headers = {
            "CodAlmacen": "Codigo",
            "NombreAlmacen": "Tienda",
            "ShortName": "Tienda",
            "ClasificacionVentaTotal": "Clas.Venta",
            "TamanoTienda": "Tamaño"
        }
        headers = list(map(lambda x: x if x not in rename_headers.keys() else rename_headers[x],
                           headers))
        self.selected_stores_model.clear()
        self.selected_stores_model.setHorizontalHeaderLabels(headers)
        for row in df_selected_stores.itertuples(index=False):
            items = [QStandardItem(str(item)) for item in row]
            self.selected_stores_model.appendRow(items)
