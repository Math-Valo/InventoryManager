from PyQt5.QtWidgets import QApplication
from controllers.cover_controller import CoverController
from controllers.date_inventory_controller import DateInventoryController
from controllers.store_controller import StoreController
from controllers.capacity_controller import CapacityController
from controllers.product_controller import ProductController
from controllers.levels_controller import LevelsController
from controllers.modify_solution_controller import ModifySolutionController
from controllers.get_modify_solution_controller import GetModifySolutionController
from controllers.download_shipments_controller import DownloadShipmentsController
from models.app_state import AppState


class NavigationController:
    def __init__(self, settings) -> None:
        self.app = QApplication([])
        self.settings = settings
        self.database_connection = None
        self.cover_controller = CoverController(self, settings)
        self.date_inventory_controller = None
        self.store_controller = None
        self.capacity_controller = None
        self.product_controller = None
        self.product_controller = None
        self.levels_controller = None
        self.modify_solution_controller = None
        self.getmodify_solution_controller = None
        self.down_load_shipments_controller = None
        self.levels = None
        self.solution = None
        self.app_state = None

    def start_application(self, database_connection):
        self.settings = self.cover_controller.settings
        self.cover_controller.close()

        self.database_connection = database_connection
        self.app_state = AppState()

        self.show_date_inventory_view()

    def show_date_inventory_view(self):
        self.date_inventory_controller = DateInventoryController(self,
                                                                 self.settings,
                                                                 self.database_connection,
                                                                 self.app_state)
        self.date_inventory_controller.show()

    def show_store_view(self, app_state, connection):
        self.app_state = app_state
        self.database_connection = connection
        self.store_controller = StoreController(self, self.settings, self.database_connection, self.app_state)

    def show_capacity_view(self, app_state, connection):
        self.app_state = app_state
        self.database_connection = connection
        self.capacity_controller = CapacityController(self, self.settings, self.database_connection, self.app_state)

    def show_product_view(self, app_state, connection):
        self.app_state = app_state
        self.database_connection = connection
        self.product_controller = ProductController(self, self.settings, self.database_connection, self.app_state)

    def phase_1(self, app_state, connection):
        self.app_state = app_state
        self.database_connection = connection
        self.levels_controller = LevelsController(self, self.settings, self.database_connection, self.app_state)

    def phase_2(self, app_state, connection, levels):
        self.app_state = app_state
        self.database_connection = connection
        self.levels = levels
        self.modify_solution_controller = ModifySolutionController(self, self.settings, self.app_state, self.levels)

    def update_solution(self, solution):
        self.solution = solution
        self.getmodify_solution_controller = GetModifySolutionController(self, self.settings, self.solution)

    def phase_3(self, solution):
        self.solution = solution
        self.down_load_shipments_controller =\
            DownloadShipmentsController(self, self.settings, self.app_state, self.solution)

    def exit_application(self):
        self.app.quit()

    def run(self):
        self.cover_controller.show()
        self.app.exec_()
