from PyQt5.QtCore import QObject, pyqtSlot
from views.cover_window import CoverWindow
from controllers.settings_controller import SettingsController
from models.database import Database
# import pandas as pd

class CoverController(QObject):

    def __init__(self):
        super().__init__()
        # Ventanas que dependen de la portada
        self.cover_window = CoverWindow()
        self.settings_controller = SettingsController()
        
        # Conexión a la base de datos
        self.settings = {
            "database_connection": Database()
        }

        # Conectar señales
        self.cover_window.start_button.clicked.connect(self.start_app)
        self.cover_window.settings_button.clicked.connect(self.open_settings)
        self.cover_window.exit_button.clicked.connect(self.close_all_windows)
        self.settings_controller.settings_applied_signal.connect(self.on_settings_applied)

    def show_cover_window(self):
        self.cover_window.show()

    def open_settings(self):
        self.settings_controller.show()

    def close_app(self):
        self.cover_window.close()
        print("App cerrada correctamente")

    def start_app(self):
        # Paso de la configuración
        self.settings["database_connection"] = self.settings_controller.database_connection
        # Cerrar todo correctamente
        self.close_all_windows()
        # Probar la conexión
        # df = self.settings["database_connection"].execute_query("last_date_in_inventory")
        # print(df)
        print("¡La aplicación ha iniciado!")    
    
    def on_settings_applied(self):
        print("La configuración ha sido aplicada.")

    @pyqtSlot()
    def close_all_windows(self):
        self.settings_controller.close_settings()
        self.cover_window.close()