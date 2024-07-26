import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt


class CoverWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Constantes
        title_app = "Nivelación de Inventarios"
        millet_brands_logo = "logo_millet_brands.png"
        abito_logo = "logo_abito.jpg"
        cover_background = "background.png"

        self.setup_ui(title_app, millet_brands_logo, abito_logo, cover_background)

    def setup_ui(self, title_name, first_logo_name, second_logo_name, background_image_name):
        self.setWindowTitle(title_name)
        self.setGeometry(100, 100, 800, 600)

        # Configuración del widget central
        self.centralwidget = QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # Ruta a la carpeta de imágenes
        self.image_dir = os.path.join(os.path.dirname(__file__), "..\\..", "images")
        self.background_image_path = os.path.join(self.image_dir, background_image_name).replace("\\", "/")

        # Crear un QLabel para la imagen de fondo
        self.background_label = QLabel(self.centralwidget)
        self.background_label.setScaledContents(True)
        self.set_background_image()

        # Crear un contenedor para los widgets
        self.widgets_container = QWidget(self.centralwidget)

        # Layout principal
        main_layout = QVBoxLayout(self.widgets_container)

        # Logos alineados a la derecha
        first_logo = QLabel()
        pixmap_first_logo = QPixmap(os.path.join(self.image_dir, first_logo_name).replace("\\", "/"))
        first_logo.setPixmap(pixmap_first_logo.scaled(100, 100, Qt.KeepAspectRatio))
        first_logo.setAlignment(Qt.AlignRight | Qt.AlignTop)

        second_logo = QLabel()
        pixmap_second_logo = QPixmap(os.path.join(self.image_dir, second_logo_name).replace("\\", "/"))
        second_logo.setPixmap(pixmap_second_logo.scaled(100, 100, Qt.KeepAspectRatio))
        second_logo.setAlignment(Qt.AlignRight | Qt.AlignTop)

        logo_layout = QVBoxLayout()
        logo_layout.addWidget(first_logo, alignment=Qt.AlignRight)
        logo_layout.addWidget(second_logo, alignment=Qt.AlignRight)
        logo_layout.addStretch()

        # Contenedor para los logos alineado a la derecha
        logo_container = QWidget()
        logo_container.setLayout(logo_layout)

        # Layout para alinear el contenedor de logos a la derecha
        logo_main_layout = QHBoxLayout()
        logo_main_layout.addStretch()
        logo_main_layout.addWidget(logo_container)

        # Botón Iniciar centrado horizontalmente en la parte inferior
        start_button_layout = QHBoxLayout()
        self.start_button = QPushButton("Iniciar")
        self.start_button.setFixedWidth(100)
        self.start_button.setFixedHeight(40)
        self.start_button.setStyleSheet("font-size: 18px; background-color: white;")
        start_button_layout.addStretch()
        start_button_layout.addWidget(self.start_button)
        start_button_layout.addStretch()

        # Layout inferior
        bottom_layout = QHBoxLayout()

        # Botón Exit
        self.exit_button = QPushButton()
        self.exit_button.setIcon(QIcon(os.path.join(self.image_dir, "exit_black.png").replace("\\", "/")))
        self.exit_button.setIconSize(self.exit_button.sizeHint())
        self.exit_button.setToolTip("Salir")

        bottom_layout.addWidget(self.exit_button, alignment=Qt.AlignLeft)

        bottom_icons_layout = QHBoxLayout()
        bottom_icons_layout.addStretch()

        # Botones de Configuración y Ayuda con Tooltips
        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon(os.path.join(self.image_dir, "settings_black.png").replace("\\", "/")))
        self.settings_button.setIconSize(self.settings_button.sizeHint())
        self.settings_button.setToolTip("Configuración")

        help_button = QPushButton()
        help_button.setIcon(QIcon(os.path.join(self.image_dir, "help_black.png").replace("\\", "/")))
        help_button.setIconSize(help_button.sizeHint())
        help_button.setToolTip("Ayuda")

        bottom_icons_layout.addWidget(self.settings_button)
        bottom_icons_layout.addWidget(help_button)

        bottom_layout.addLayout(bottom_icons_layout)

        # Añadir widgets al layout principal
        main_layout.addLayout(logo_main_layout)
        main_layout.addStretch()
        main_layout.addLayout(start_button_layout)
        main_layout.addLayout(bottom_layout)

        # Asegurar que el layout principal sea el layout
        self.widgets_container.setLayout(main_layout)

        # Ajustar el contenedor de widgets y el QLabel de fondo
        self.update_background_and_widgets()

    def set_background_image(self):
        pixmap = QPixmap(self.background_image_path)
        self.background_label.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_background_and_widgets()

    def update_background_and_widgets(self):
        self.background_label.resize(self.centralwidget.size())
        self.widgets_container.resize(self.centralwidget.size())
