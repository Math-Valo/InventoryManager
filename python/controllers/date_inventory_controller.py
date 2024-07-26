from views.date_inventory_window import DateInventoryWindow


class DateInventoryController:
    def __init__(self, navigation_controller, settings, database_connection, app_state) -> None:
        self.navigation_controller = navigation_controller
        self.settings = settings
        self.app_state = app_state
        self.connection = database_connection
        self.last_date_in_inventory = self.get_last_date()
        self.view = DateInventoryWindow(self.last_date_in_inventory)
        self.setup_connections()

    def setup_connections(self):
        self.view.reset_date_button.clicked.connect(self.reset_date)
        self.view.continue_button.clicked.connect(self.continue_to_next_window)

    def show(self):
        self.view.show()

    def get_last_date(self):
        query = "last_date_in_inventory"
        df = self.connection.execute_query(query)
        if not df.empty:
            return df.iloc[0, 0]

    def reset_date(self):
        self.view.set_date(self.last_date_in_inventory)

    def continue_to_next_window(self):
        selected_date = self.get_date()
        self.navigation_controller.show_store_view(selected_date)

    def get_date(self):
        return self.view.date_edit.date().toString("yyyy-MM-dd")

    def close(self):
        self.view.close()
