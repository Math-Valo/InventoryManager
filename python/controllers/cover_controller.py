from PyQt5.QtCore import pyqtSignal
from views.cover_window import CoverWindow
from controllers.settings_controller import SettingsController
from models.database import Database
from PyQt5.QtWidgets import QMessageBox


class CoverController:
    def __init__(self, navigation_controller, settings):
        self.navigation_controller = navigation_controller
        self.settings = settings
        self.database_connection = Database()
        self.view = CoverWindow()
        self.settings_controller = SettingsController(self.settings)
        self.setup_connections()

    def setup_connections(self):
        self.view.exit_button.clicked.connect(self.exit_application)
        self.view.start_button.clicked.connect(self.start_application)
        self.view.settings_button.clicked.connect(self.open_settings_window)
        self.settings_controller.settings_applied_signal.connect(self.on_settings_applied)

    def open_settings_window(self):
        self.settings_controller.show()

    def exit_application(self):
        self.navigation_controller.exit_application()

    def on_settings_applied(self):
        credentials = self.settings.settings.get("credentials")
        host = credentials.get("host", "")
        database = credentials.get("database", "")
        user = credentials.get("user", "")
        password = credentials.get("password", "")
        port = credentials.get("port", "")
        driver = credentials.get("driver", "")
        self.database_connection.set_credentials(host, database, user, password, port, driver)

    def start_application(self):
        self.settings_controller.close()
        if not self.database_connection.connect():
            pyqtSignal
            QMessageBox.warning(self.view, 'Error', 'No se pudo conectar a la base de datos.')
        self.navigation_controller.star_application(self.database_connection)
    
    def close(self):
        self.view.close()

    def show(self):
        self.view.show()
