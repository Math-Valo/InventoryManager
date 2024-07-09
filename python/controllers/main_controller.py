from PyQt5.QtWidgets import QMessageBox
from views.cover_window import CoverWindow
from views.settings_window import SettingsWindow

class MainController:
    def __init__(self):
        self.cover_window = CoverWindow()
        self.cover_window.start_button.clicked.connect(self.start_app)
        self.cover_window.settings_button.clicked.connect(self.open_settings)
        self.cover_window.exit_button.clicked.connect(self.cover_window.close)
        self.settings_window = None

    def show_main_window(self):
        self.cover_window.show()

    # def close_app(self):
    #     self.

    def start_app(self):
        self.cover_window.close()
        print("¡La aplicación ha iniciado!")
    
    def open_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.test_button.clicked.connect(self.verify_connection)
        self.settings_window.show()

    def verify_connection(self):
        print("Agregar verificación de conexión")