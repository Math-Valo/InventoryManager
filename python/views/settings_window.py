import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, 
    QTabWidget, QLineEdit, QLabel, QCheckBox, QMessageBox
)
from PyQt5.QtCore import pyqtSlot
import hashlib

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Aplicación Principal")
        
        self.button = QPushButton("Cambiar Configuración", self)
        self.button.clicked.connect(self.openSettings)

        self.setCentralWidget(self.button)
        self.setGeometry(100, 100, 800, 600)

    def openSettings(self):
        self.close()
        self.settings_window = SettingsWindow()
        self.settings_window.show()

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Configuración")
        
        # Crear ventana con pestañas
        self.tabs = QTabWidget()
        
        # Pestaña de configuración de la base de datos
        self.db_tab = QWidget()
        # Otras pestañas (para ejemplificar, aquí se tiene para el color de fondo)
        # self.color_tab = QWidget()
        
        self.tabs.addTab(self.db_tab, "Credenciales a Base de Datos")
        # self.tabs.addTab(self.color_tab, 'Color de Fondo')
        
        self.db_tab_ui()
        # self.color_tab_ui()
        
        self.setCentralWidget(self.tabs)
        self.setGeometry(100, 100, 800, 600)

    def db_tab_ui(self):
        # Layout principal
        layout = QVBoxLayout()
        
        self.server_label = QLabel("Servidor:")
        self.server_input = QLineEdit()
        layout.addWidget(self.server_label)
        layout.addWidget(self.server_input)

        self.db_label = QLabel("Base de datos:")
        self.db_input = QLineEdit()
        layout.addWidget(self.db_label)
        layout.addWidget(self.db_input)

        self.user_label = QLabel("Usuario:")
        self.user_input = QLineEdit()
        layout.addWidget(self.user_label)
        layout.addWidget(self.user_input)
        
        self.pass_label = QLabel("Contraseña:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_label)
        layout.addWidget(self.pass_input)

        self.port_label = QLabel("Puerto (opcional):")
        self.port_input = QLineEdit()
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)

        self.driver_label = QLabel("Driver (opcional):")
        self.driver_input = QLineEdit()
        layout.addWidget(self.driver_label)
        layout.addWidget(self.driver_input)

        self.save_checkbox = QCheckBox("Establecer credenciales por defecto")
        layout.addWidget(self.save_checkbox)
        
        self.test_button = QPushButton("Verificar Conexión")
        # self.test_button.clicked.connect(self.verify_connection)
        layout.addWidget(self.test_button)
        
        self.db_tab.setLayout(layout)

    # def color_tab_ui(self):
    #     layout = QVBoxLayout()
    #     self.color_label = QLabel('Esta es la pestaña para cambiar el color de fondo.')
    #     layout.addWidget(self.color_label)
    #     self.color_tab.setLayout(layout)

    # @pyqtSlot()
    # def verify_connection(self):
    #     server = self.server_input.text()
    #     db = self.db_input.text()
    #     user = self.user_input.text()
    #     password = self.pass_input.text()
    #     port = self.port_input.text()
    #     driver = self.driver_input.text()
    # 
    #     # Queda por agregar el código para verificar la conexión a la base de datos
    #     # Esta es una simulación de la verificación de conexión
    #     if user == "admin" and password == "admin":
    #         QMessageBox.information(self, "Éxito", "Conexión exitosa.")
    #         if self.save_checkbox.isChecked():
    #             self.save_credentials(server, db, user, password, port, driver)
    #     else:
    #         QMessageBox.warning(self, "Error", "Conexión fallida.")

    # def save_credentials(self, server, db, user, password, port, driver):
    #     hashed_password = hashlib.sha256(password.encode()).hexdigest()
    #     # Guardar las credenciales (con la contraseña hash) en un archivo o base de datos segura
    #     with open("credentials.txt", "w") as file:
    #         file.write(f"{user}:{hashed_password}")
    #     QMessageBox.information(self, "Guardado", "Credenciales guardadas de manera segura.")
    #     with open("credentials.txt", "w") as file:
    #         file.write(f"""
    #             DRIVER={{{driver}}};
    #             SERVER={server};
    #             PORT={port};
    #             DATABASE={db};
    #             UID={user};
    #             PASSWORD={hashed_password};
    #         """
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
