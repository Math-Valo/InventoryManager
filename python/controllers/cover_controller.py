from PyQt5.QtCore import pyqtSignal, QObject
from views.cover_window import CoverWindow
from views.settings_window import SettingsWindow

class CoverController(QObject):
    # show_cover_window = pyqtSignal()
    close_settings_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Ventanas que dependen de la portada
        self.cover_window = CoverWindow()
        self.settings_window = SettingsWindow()
        # Conectar señales
        self.cover_window.start_button.clicked.connect(self.start_app)
        self.cover_window.settings_button.clicked.connect(self.open_settings)
        self.cover_window.exit_button.clicked.connect(self.cover_window.close)
        self.close_settings_signal.connect(self.settings_window.close)

    def show_cover_window(self):
        self.cover_window.show()

    # def close_app(self):
    #     self.

    def start_app(self):
        self.close_settings_signal.emit()
        self.cover_window.close()
        print("¡La aplicación ha iniciado!")
    
    def open_settings(self):
        self.settings_window.show()
