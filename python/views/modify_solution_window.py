import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QDialogButtonBox, QApplication, QPushButton, QFileDialog, \
    QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class ModifySolutionWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.button_select_path = QPushButton()
        self.path_display = QLabel()
        self.selected_directory = QFileDialog
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Confirmar cambios manuales")
        self.setGeometry(100, 100, 400, 200)

        # Layout principal
        layout = QVBoxLayout()

        # Modificación de la fuente
        font = QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)

        # Etiqueta con la pregunta
        question_label = QLabel("¿Desea realizar cambios antes de continuar?")
        question_label.setFont(font)
        question_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(question_label)

        # Etiqueta informativa para la ubicación donde se guardará el archivo
        path_label = QLabel("El archivo se guardará en la siguiente ubicación:")
        layout.addWidget(path_label)

        # Etiqueta informativa para la ubicación del archivo
        file_dir = os.path.join(os.path.dirname(__file__), "..\\..", "files")
        self.path_display.setText(file_dir + "\\Nivelacion_modificable.xlsx")
        layout.addWidget(self.path_display)

        # Botón para seleccionar la ubicación de guardado
        self.button_select_path.setText("Cambiar ubicación de guardado")
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
    window = ModifySolutionWindow()
    window.show()
    sys.exit(app.exec_())
