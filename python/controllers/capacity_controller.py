from views.capacity_window import CapacityWindow


class CapacityController:
    def __init__(self, navigation_controller, settings, database_connection, app_state) -> None:
        self.navigation_controller = navigation_controller
        self.settings = settings
        self.app_state = app_state
        self.connection = database_connection

        self.df_store = self.app_state.get_store_dimensions()
        self.df_store_filtered = self.df_store[self.df_store["Canal"] == "TIENDAS PROPIAS"]
        self.df_store_filtered["ShortName"] = \
            self.df_store_filtered["NombreAlmacen"].str.replace("ABITO ", "").str.replace("AEROPUERTO ", "")

        self.view = CapacityWindow(self.df_store_filtered)
        self.setup_connections()
        self.show()

    def setup_connections(self):
        for row in range(self.view.table.rowCount()):
            spinbox = self.view.table.cellWidget(row, 1)
            spinbox.valueChanged.connect(lambda _, r=row: self.update_stock_colors(r))
        self.view.continue_button.clicked.connect(self.continue_to_next_window)

    def update_stock_colors(self, row):
        capacity = self.view.table.cellWidget(row, 1).value()
        stock = int(self.view.table.item(row, 2).text())
        stock_item = self.view.table.item(row, 2)
        self.view.set_stock_color(stock_item, capacity, stock)

    def continue_to_next_window(self):
        self.navigation_controller.show_product_view(self.app_state, self.connection)
        self.view.close()

    def show(self):
        self.view.show()
