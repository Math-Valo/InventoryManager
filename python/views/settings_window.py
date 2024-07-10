from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QTabWidget, QLineEdit, QLabel, QCheckBox
from controllers.settings_controller import SettingsController


class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.controller = SettingsController(self)

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
        self.server_input.setText("108.175.14.162")
        layout.addWidget(self.server_label)
        layout.addWidget(self.server_input)

        self.db_label = QLabel("Base de datos:")
        self.db_input = QLineEdit()
        self.db_input.setText("DBABITOMSQL")
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
        self.port_input.setText("3306")
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)

        self.driver_label = QLabel("Driver (opcional):")
        self.driver_input = QLineEdit()
        self.driver_input.setText("MySQL ODBC 8.4 ANSI Driver")
        layout.addWidget(self.driver_label)
        layout.addWidget(self.driver_input)

        self.save_checkbox = QCheckBox("Establecer credenciales por defecto")
        layout.addWidget(self.save_checkbox)
        
        self.test_button = QPushButton("Verificar Conexión")
        layout.addWidget(self.test_button)
        
        self.db_tab.setLayout(layout)
