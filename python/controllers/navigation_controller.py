from PyQt5.QtWidgets import QApplication
from controllers.cover_controller import CoverController
from controllers.settings_controller import SettingsController
from controllers.date_inventory_controller import DateInventoryController


class NavigationController:
    def __init__(self, settings) -> None:
        self.app = QApplication([])
        self.settings = settings
        self.cover_controller = CoverController(self, settings)

    def star_application(self, database_connection):
        self.cover_controller.close()
        print("Se ha iniciado la aplicación")
        # Iniciar la lógica de la aplicación de neogio

    def exit_application(self):
        self.app.quit()

    def run(self):
        self.cover_controller.show()
        self.app.exec_()