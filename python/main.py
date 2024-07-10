import sys
from PyQt5.QtWidgets import QApplication
from controllers.cover_controller import CoverController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cover_controller = CoverController()
    cover_controller.show_cover_window()
    sys.exit(app.exec_())
