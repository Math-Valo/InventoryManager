from views.store_window import StoreWindow
from PyQt5.QtWidgets import QLabel


class StoreController:
    def __init__(self, navigation_controller, settings, database_connection, app_state) -> None:
        self.navigation_controller = navigation_controller
        self.settings = settings
        self.app_state = app_state
        self.connection = database_connection

        self.df_store = self.app_state.get_store_dimensions()
        self.df_store["ShortName"] = \
            self.df_store["NombreAlmacen"].str.replace("ABITO ", "").str.replace("AEROPUERTO ", "")

        self.view = StoreWindow(self.df_store)
        self.setup_connections()
        self.show()

    def setup_connections(self):
        for region, checkbox in self.view.regions.items():
            checkbox.clicked.connect(lambda checked, region=region: self.select_unselect_region(checked, region))
        for code, checkbox in self.view.stores.items():
            checkbox.clicked.connect(lambda checked, code=code: self.select_unselect_store(checked, code))
        self.view.continue_button.clicked.connect(self.continue_to_next_window)

    def select_unselect_region(self, checked, region):
        stores = self.df_store[self.df_store["Region"]==region]["CodAlmacen"].tolist()
        for store in stores:
            self.view.stores[store].setChecked(checked)
 
        self.update_selected_stores()

    def select_unselect_store(self, checked, code):
        region = self.df_store[self.df_store["CodAlmacen"]==code]["Region"].iat[0]
        if checked:
            for store in self.df_store[self.df_store["Region"]==region]["CodAlmacen"].tolist():
                if not self.view.stores[store].isChecked():
                    return None
            self.view.regions[region].setChecked(True)
        else:
            self.view.regions[region].setChecked(False)
 
        self.update_selected_stores()
    
    def update_selected_stores(self):
        headers = ["CodAlmacen", "ShortName", "Region", "Ciudad", "Zona",
                  "ClasificacionVentaTotal", "TamanoTienda", "Capacidad"]
        selected_stores = self.get_stores_list()
        query = "CodAlmacen in "+selected_stores.__str__()
        df_selected_stores = self.df_store[headers].query(query)
        self.view.update_selected_stores(df_selected_stores)

    def get_stores_list(self):
        selected_stores = list()
        for code, checkbox in self.view.stores.items():
            if checkbox.isChecked():
                selected_stores.append(code)
        return selected_stores

    def continue_to_next_window(self):
        selected_stores = self.get_stores_list()
        query = "CodAlmacen in "+selected_stores.__str__()
        df_selected_stores = self.df_store.query(query)
        self.app_state.set_store_dimensions(df_selected_stores)
        self.connection.update_query_stores(selected_stores)
        self.app_state.set_product_dimensions(self.get_product_dimension())
        self.navigation_controller.show_product_view(self.app_state, self.connection)

    def get_product_dimension(self):
        query = "products_in_inventory"
        return self.connection.execute_query(query)

    def show(self):
        self.view.show()

    def close(self):
        self.view.close()
