from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QScrollArea, QCheckBox


class StoreWindow(QWidget):
    def __init__(self, df_store) -> None:
        super().__init__()
        self.df_store = df_store

        self.region_checkboxes = dict()
        self.stores_checkboxes = dict()

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Tiendas a nivelar")
        # self.setGeometry(100, 100, 490, 475)

        # Layout principal
        layout = QVBoxLayout()

        # Layout del proceso
        process_layout = QHBoxLayout()

        # Layout para seleccionar tiendas y tiendas seleccionadas
        selection_layout = QVBoxLayout()
        selected_layout = QVBoxLayout()

        # Espacio que se llenará de checkbox para seleccionar las regiones
        region_selection_list = QScrollArea()
        region_selection_layout = QVBoxLayout()
        region_selection_list.setLayout(region_selection_layout)

        # Espacio que se llenará de checkbox para seleccionar las tiendas
        store_selection_list = QScrollArea()
        store_selection_layout = QVBoxLayout()
        store_selection_list.setLayout(store_selection_layout)

        # Espacio que se llenará con las tiendas ya seleccionadas
        selected_store_list = QScrollArea()
        selected_store_layout = QVBoxLayout()
        selected_store_list.setLayout(selected_store_layout)

        # Llenado de las tiendas y las regiones
        regions = self.df_store["Region"].unique()
        for region in regions:
            checkbox = QCheckBox(region)
            region_selection_layout.addWidget(checkbox)
            self.region_checkboxes[region] = checkbox

        for _, row in self.df_store.iterrows():
            checkbox = QCheckBox(f"{row['CodAlmacen']} - {row['NombreAlmacen']}")
            store_selection_layout.addWidget(checkbox)
            self.region_checkboxes[row["CodAlmacen"]] = checkbox

        # Botón para terminar selección
        self.continue_button = QPushButton("Continuar >>>")

        # Llenado de layouts
        selection_layout.addWidget(region_selection_list)
        selection_layout.addWidget(store_selection_list)

        selected_layout.addWidget(QLabel("Tiendas seleccionadas:"))
        selected_layout.addWidget(selected_store_list)

        process_layout.addLayout(selection_layout)
        process_layout.addLayout(selected_layout)

        layout.addLayout(process_layout)
        layout.addWidget(self.continue_button)

        self.setLayout(layout)


if __name__ == "__main__":
    import sys
    import pandas as pd
    from PyQt5.QtWidgets import QApplication
    try:
        app = QApplication().instance()
    except:
        app = None
    if app is None:
        app = QApplication(sys.argv)
    df = pd.DataFrame({"CodAlmacen": ["001", "002", "003"],
                       "NombreAlmacen": ["T1", "T2", "T3"],
                       "Region": ["R1", "R1", "R2"]})
    view = StoreWindow(df)
    view.show()
    sys.exit(app.exec_())
