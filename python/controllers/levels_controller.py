from views.levels_window import LevelsWindow
from models.phase_1 import Phase1


class LevelsController:
    def __init__(self, navigation_controller, settings, database_connection, app_state) -> None:
        self.navigation_controller = navigation_controller
        self.settings = settings
        self.app_state = app_state
        self.connection = database_connection

        print("Fase 1: Determinación de los niveles por tiendas")
        self.df_facts = self.app_state.get_facts()
        store_product_tuples = self.df_facts[["CodAlmacen", "SKU"]].apply(tuple, axis=1).tolist()
        self.connection.update_query_store_product(store_product_tuples)
        self.app_state.setup_kpis(self.get_quarters())
        self.levels = Phase1(self.app_state.get_store_dimensions(), self.app_state.get_facts())

        levels_modified = self.levels.store_profile.copy()
        levels_modified["ShortName"] = \
            levels_modified["NombreAlmacen"].str.replace("ABITO ", "").str.replace("AEROPUERTO ", "")
        self.view = LevelsWindow(levels_modified, self.levels)
        self.setup_connections()
        self.show()

    def setup_connections(self):
        for row in range(self.view.table.rowCount()):
            spinbox = self.view.table.cellWidget(row, 4)
            spinbox.valueChanged.connect(lambda level, r=row: self.update_table(level, r))
        self.view.continue_button.clicked.connect(self.continue_to_next_window)

    def update_table(self, level, row):
        # Tienda actual
        store_label = self.view.table.item(row, 0).text()
        store_cod = store_label.split(" - ")[0]
        store_profile = self.levels.store_profile[self.levels.store_profile["CodAlmacen"] == store_cod]
        # Variables
        capacity = int(self.view.table.item(row, 2).text())
        stock = store_profile["Stock"].iloc[0]
        fashion_stock = store_profile["CurrentInventory"].iloc[0]
        average_sales = store_profile["AvgMonthlySalesLastQuarter"].iloc[0]
        if average_sales != 0:
            new_coverage = (fashion_stock + level)/average_sales
        else:
            new_coverage = -1
        stock_item = self.view.table.item(row, 5)
        fashion_stock_item = self.view.table.item(row, 6)
        coverage_item = self.view.table.item(row, 7)
        # Actualización de los valores
        self.view.table.item(row, 5).setText(str(stock + level))
        self.view.table.item(row, 6).setText(str(fashion_stock + level))
        self.view.table.item(row, 7).setText(str(new_coverage))
        # Actualización de colores
        self.view.set_stock_color(stock_item, capacity, stock, level)
        self.view.set_fashion_stock_color(fashion_stock_item, fashion_stock, level)
        self.view.set_coverage_color(coverage_item, fashion_stock, average_sales, level)
        # Actualización de la cantidad fuera de la tienda
        total_levels = 0
        for row in range(self.view.table.rowCount()):
            total_levels += self.view.table.cellWidget(row, 4).value()
        self.view.sum_expected_level.setText(f"Fuera de tienda = {total_levels}")
        if total_levels != 0:
            self.view.sum_expected_level.setStyleSheet("color")
        self.view.set_total_levels_color(total_levels)

    def continue_to_next_window(self):
        total_levels = 0
        for row in range(self.view.table.rowCount()):
            total_levels += self.view.table.cellWidget(row, 4).value()
        if total_levels != 0:
            return None
        for row in range(self.view.table.rowCount()):
            store_label = self.view.table.item(row, 0).text()
            store_cod = store_label.split(" - ")[0]
            level = self.view.table.cellWidget(row, 4).value()
            self.levels.store_profile.loc[self.levels.store_profile["CodAlmacen"] == store_cod, "ExpectedLevel"] = level
        self.close()
        self.navigation_controller.phase_2(self.app_state, self.connection, self.levels)

    def show(self):
        self.view.show()

    def close(self):
        self.view.close()

    def get_quarters(self):
        query = "quarter_sales"
        return self.connection.execute_query(query)
