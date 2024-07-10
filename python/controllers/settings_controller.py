from PyQt5.QtWidgets import QMessageBox
# from models.database import Database

class SettingsController:
    def __init__(self, settings_window):
        self.settings_window = settings_window
        self.settings_window.test_button.clicked.connect(self.verify_connection)

    def verify_connection(self):
        host = self.settings_window.server_input.text()
        database = self.settings_window.db_input.text()
        user = self.settings_window.user_input.text()
        password = self.settings_window.pass_input.text()
        port = self.settings_window.port_input.text()
        driver = self.settings_window.driver_input.text()

        print(f"""
            Host: {host}
            DB: {database}
            User: {user}
            Pass: {password}
            Port: {port}
            Driver: {driver}
        """)

        # self.database = Database(host, user, password, database)
        # if self.database.connect():
        #     QMessageBox.information(self.settings_window, 'Éxito', 'Conexión exitosa.')
        #     if self.settings_window.save_checkbox.isChecked():
        #         self.database.save_credentials(user, password)
        # else:
        #     QMessageBox.warning(self.settings_window, 'Error', 'Conexión fallida.')
