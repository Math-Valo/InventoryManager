import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QDialogButtonBox, QPushButton, QFileDialog, QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class DownloadShipmentsWindow(QWidget):
    def __init__(self, file) -> None:
        super().__init__()
        self.button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.button_select_path = QPushButton()
        self.path_display = QLabel()
        self.selected_directory = QFileDialog
        self.selected_file = file
        self.find_files_folder()
        self.setup_ui()

    def find_files_folder(self, files_folder="files"):
        current_path = os.path.dirname(__file__)
        while not os.path.exists(os.path.join(current_path, files_folder)):
            parent_path = os.path.dirname(current_path)
            if current_path == parent_path:
                raise FileNotFoundError(f"No se pudo encontrar {files_folder}")
            current_path = parent_path
        self.selected_file = os.path.join(current_path, files_folder, self.selected_file)

    def setup_ui(self):
        self.setWindowTitle('Descargar envíos')
        self.setGeometry(100, 100, 400, 200)

        # Layout principal
        layout = QVBoxLayout()

        # Modificación de la fuente
        font = QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)

        # Etiqueta con la pregunta
        question_label = QLabel("¿Desea guardar los envíos en un arhivo .xlsx?")
        question_label.setFont(font)
        question_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(question_label)

        # Etiqueta informativa para la ubicación donde se descargará el archivo
        path_label = QLabel("El archivo se guardará en la siguiente ubicación:")
        layout.addWidget(path_label)

        # Etiqueta informativa para la ubicación del archivo
        self.path_display.setText(self.selected_file)
        layout.addWidget(self.path_display)

        # Botón para seleccionar la ubicación de guardado
        self.button_select_path.setText("Cambiar ubicación de descarga")
        layout.addWidget(self.button_select_path)

        # Botones de respuestas
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setCenterButtons(True)
        layout.addWidget(self.button_box)

        # Aplicar el layout
        self.setLayout(layout)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = DownloadShipmentsWindow("test.xlsx")
    window.show()
    sys.exit(app.exec_())
