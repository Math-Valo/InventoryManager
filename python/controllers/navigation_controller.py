from PyQt5.QtWidgets import QApplication
from controllers.cover_controller import CoverController
from controllers.date_inventory_controller import DateInventoryController
from models.app_state import AppState


class NavigationController:
    def __init__(self, settings) -> None:
        self.app = QApplication([])
        self.settings = settings
        self.database_connection = None
        self.cover_controller = CoverController(self, settings)
        self.date_inventory_controller = None

    def start_application(self, database_connection):
        self.settings = self.cover_controller.settings
        self.cover_controller.close()

        self.database_connection = database_connection

        self.app_state = AppState()
        self.app_state.set_store_dimensions(self.get_store_dimension())
        self.app_state.set_product_dimensions(self.get_prduct_dimension())

        self.show_date_inventory_view()

    def show_date_inventory_view(self):
        self.date_inventory_controller = DateInventoryController(self, self.settings, self.database_connection)
        self.date_inventory_controller.show()

    def show_store_view(self, inventory_date):
        self.app_state.set_inventory_date(inventory_date)
        self.date_inventory_controller.close()
        print("Fecha:")
        print(self.app_state.inventory_date)
        print("Tiendas:")
        print(self.app_state.store_dimensions)
        print("Productos:")
        print(self.app_state.product_dimensions)
        self.exit_application()
        # self.store_controller = StoreController(self)

    def exit_application(self):
        self.app.quit()

    def run(self):
        self.cover_controller.show()
        self.app.exec_()

    # Mala práctica: navigation_controller debe de ser para navegar de una ventana a otra,
    # no para obtener datos y actualizar valores al app_state
    def get_store_dimension(self):
        query = "stores_in_inventory"
        return self.database_connection.execute_query(query)

    def get_prduct_dimension(self):
        query = "products_in_inventory"
        return self.database_connection.execute_query(query)

    def get_inventory_and_sales_data(self):
        query = "inventories_and_sales"
