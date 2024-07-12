from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject
from models.database import Database
from views.settings_window import SettingsWindow


# ToDo: cambiar las ventanas de alerta por acciones de un módulo para vistas de alertas

class SettingsController(QObject):
    settings_applied_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.database_connection = Database()
        self.settings_window = SettingsWindow()
        self.settings_window.test_connection_button.clicked.connect(self.verify_connection)
        self.settings_window.apply_settings_buttom.clicked.connect(self.apply_settings)
        self.settings_window.close_buttom.clicked.connect(self.close_settings)

    def show(self):
        self.settings_window.show()

    def verify_connection(self):
        host = self.settings_window.server_input.text()
        database = self.settings_window.db_input.text()
        user = self.settings_window.user_input.text()
        password = self.settings_window.pass_input.text()
        port = self.settings_window.port_input.text()
        driver = self.settings_window.driver_input.text()

        self.database_connection.set_credentials(host, database, user, password, port, driver)
        if self.database_connection.connect():
            QMessageBox.information(self.settings_window, 'Éxito', 'Conexión exitosa.')
            # if self.settings_window.save_checkbox.isChecked():
            #     self.database.save_credentials(user, password)
        else:
            QMessageBox.warning(self.settings_window, 'Error', 'Conexión fallida.')

    def apply_settings(self):
        host = self.settings_window.server_input.text()
        database = self.settings_window.db_input.text()
        user = self.settings_window.user_input.text()
        password = self.settings_window.pass_input.text()
        port = self.settings_window.port_input.text()
        driver = self.settings_window.driver_input.text()

        self.database_connection.set_credentials(host, database, user, password, port, driver)

        self.settings_applied_signal.emit()

        print("Configuración aplicada")

    def close_settings(self):
        self.settings_window.close()