from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal
from models.database import Database
from views.settings_window import SettingsWindow


class SettingsController(QObject):
    settings_applied_signal = pyqtSignal()

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.database_connection = Database()
        self.view = SettingsWindow(self.settings)
        self.load_credentials()
        self.setup_connections()

    def setup_connections(self):
        self.view.test_connection_button.clicked.connect(self.verify_connection)
        self.view.apply_settings_buttom.clicked.connect(self.apply_settings)
        self.view.close_buttom.clicked.connect(self.close)

    def show(self):
        self.view.show()

    def verify_connection(self):
        host = self.view.server_input.text()
        database = self.view.db_input.text()
        user = self.view.user_input.text()
        password = self.view.pass_input.text()
        port = self.view.port_input.text()
        driver = self.view.driver_input.text()

        self.database_connection.set_credentials(host, database, user, password, port, driver)
        if self.database_connection.connect():
            QMessageBox.information(self.view, 'Éxito', 'Conexión exitosa.')
            # if self.view.save_checkbox.isChecked():
            #     self.database.save_credentials(user, password)
        else:
            QMessageBox.warning(self.view, 'Error', 'Conexión fallida.')

    def get_credentials(self):
        return {
            "host": self.view.server_input.text(),
            "database": self.view.db_input.text(),
            "user": self.view.user_input.text(),
            "password": self.view.pass_input.text(),
            "port": self.view.port_input.text(),
            "driver": self.view.driver_input.text()
        }

    def set_credentials(self, credentials):
        self.view.server_input.setText(credentials.get("host", ""))
        self.view.db_input.setText(credentials.get("database", ""))
        self.view.user_input.setText(credentials.get("user", ""))
        self.view.pass_input.setText(credentials.get("password", ""))
        self.view.port_input.setText(credentials.get("port", ""))
        self.view.driver_input.setText(credentials.get("driver", ""))

    def apply_settings(self):
        credentials = self.get_credentials()
        self.database_connection.set_credentials(
            credentials.get("host", ""),
            credentials.get("database", ""),
            credentials.get("user", ""),
            credentials.get("password", ""),
            credentials.get("port", ""),
            credentials.get("driver", "")
        )
        self.settings_applied_signal.emit()
        self.settings.set_settings("credentials", credentials)

    def load_credentials(self):
        credentials = self.settings.get_settings("credentials")
        if credentials:
            self.set_credentials(credentials)

    def close(self):
        self.view.close()
