from views.date_inventory_window import DateInventoryWindow
from PyQt5 import QtCore

class DateInventoryController:
    def __init__(self, navigation_controller, settings, app_state=None) -> None:
        self.navigation_controller = navigation_controller
        self.settings = settings
        self.app_state = app_state
        self.view = DateInventoryWindow(self)
        self.connection = self.settings.get("database_connection")
        self.view.setup_ui()

    def show_date_inventory_window(self):
        self.view.show()

    def get_last_date(self):
        query = "last_date_in_inventory"
        df = self.connection.execute_query(query)
        if not df.empty:
            return df.iloc[0, 0]
        return ""

    def setup_connections(self):
        self.view.reset_date_button.clicked.connect(self.reset_date)
        self.view.continue_button.clicked.connect(self.get_data)

    def reset_date(self):
        self.view.set_date(self.get_last_date)

    def continue_to_next_window(self):
        # self.navigation_controller
        selected_date = self.view.date_edit.date()
        print(selected_date)
        print("¡Continua a la siguiente página!")
