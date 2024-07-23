from PyQt5.QtWidgets import QApplication
from controllers.cover_controller import CoverController
from views.date_inventory_window import DateInventoryWindow

class NavigationController:
    def __init__(self) -> None:
        self.current_window = None

    def show_cover_window(self):
        if self.current_window:
            self.current_window.close()
        self.current_window = CoverController(self)
        self.current_window.show_cover_window()

    def show_date_inventory_window(self, settings_cover):
        if self.show_cover_window:
            self.current_window.close()
        self.current_window = DateInventoryWindow(self, settings_cover)
        self.current_window.show()

    def close_application(self):
        if self.current_window:
            self.current_window.close()
        QApplication.instance().quit()