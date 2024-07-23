from PyQt5.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLineEdit, QLabel, QFormLayout, QCheckBox
)
# from controllers.settings_controller import SettingsController


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
       #  self.controller = SettingsController(self)

    def setup_ui(self):
        self.setWindowTitle("Configuración")
        self.setGeometry(100, 100, 600, 800)

        # Layout principal
        main_layout = QVBoxLayout()

        # Crear ventana con pestañas
        self.tabs = QTabWidget()
        
        # Pestaña de configuración de la base de datos
        self.db_tab = QWidget()
        # Otras pestañas (para ejemplificar, aquí se tiene para el color de fondo)
        # self.color_tab = QWidget()
        
        self.tabs.addTab(self.db_tab, "Credenciales a Base de Datos")
        # self.tabs.addTab(self.color_tab, 'Color de Fondo')
        main_layout.addWidget(self.tabs)

        # Configurar cada pestaña
        self.db_tab_ui()
        # self.color_tab_ui()
        
        # Layout ocn botones de la ventana de settings, independiente de las pestañas
        settings_buttoms_layout = QHBoxLayout()

        self.apply_settings_buttom = QPushButton("Aplicar configuración")
        self.close_buttom = QPushButton("Cerrar")
        settings_buttoms_layout.addStretch()
        settings_buttoms_layout.addWidget(self.apply_settings_buttom)
        settings_buttoms_layout.addWidget(self.close_buttom)

        # Acomodar todo en el layout principal
        main_layout.addLayout(settings_buttoms_layout)
        self.setLayout(main_layout)


    def db_tab_ui(self):
        # Layout del formulario para las credenciales
        layout_form = QFormLayout()

        # Elementos del formulario        
        self.server_input = QLineEdit()
        # self.server_input.setText("108.175.14.162")

        self.db_input = QLineEdit()
        # self.db_input.setText("DBABITOMSQL")

        self.user_input = QLineEdit()
        
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)

        self.port_input = QLineEdit()
        # self.port_input.setText("3306")

        self.driver_input = QLineEdit()
        # self.driver_input.setText("MySQL ODBC 8.4 ANSI Driver")

        layout_form.addRow(QLabel("Servidor"), self.server_input)
        layout_form.addRow(QLabel("Base de datos:"), self.db_input)
        layout_form.addRow(QLabel("Usuario:"), self.user_input)
        layout_form.addRow(QLabel("Contraseña:"), self.pass_input)
        layout_form.addRow(QLabel("Puerto (opcional):"), self.port_input)
        layout_form.addRow(QLabel("Driver (opcional):"), self.driver_input)

        # Botones de interacción de las credenciales.
        self.save_checkbox = QCheckBox("Establecer credenciales por defecto")
        self.test_connection_button = QPushButton("Verificar Conexión")
        # layout_form.addWidget(self.save_checkbox)
        layout_form.addWidget(self.test_connection_button)
        
        self.db_tab.setLayout(layout_form)
