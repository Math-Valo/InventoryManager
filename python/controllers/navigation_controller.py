from PyQt5.QtWidgets import QApplication
from controllers.cover_controller import CoverController
from controllers.date_inventory_controller import DateInventoryController
from models.app_state import AppState


class NavigationController:
    def __init__(self, settings) -> None:
        self.app = QApplication([])
        self.settings = settings
        self.cover_controller = CoverController(self, settings)
        self.date_inventory_controller = None

    def star_application(self, database_connection):
        self.settings = self.cover_controller.settings
        self.cover_controller.close()

        self.app_state = AppState()

        self.date_inventory_controller = DateInventoryController(self, self.settings, database_connection, self.app_state)
        self.date_inventory_controller.show()

    def exit_application(self):
        self.app.quit()

    def run(self):
        self.cover_controller.show()
        self.app.exec_()