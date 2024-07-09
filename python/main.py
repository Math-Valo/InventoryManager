import sys
from PyQt5.QtWidgets import QApplication
from controllers.main_controller import MainController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_controller = MainController()
    main_controller.show_main_window()
    sys.exit(app.exec_())
