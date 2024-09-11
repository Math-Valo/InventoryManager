from views.product_window import ProductWindow


class ProductController:
    def __init__(self, navigation_controller, settings, database_connection, app_state) -> None:
        self.navigation_controller = navigation_controller
        self.settings = settings
        self.app_state = app_state
        self.connection = database_connection

        self.df_product = self.app_state.get_product_dimensions()
        self.df_product_filtered = self.df_product

        headers = ["SKU", "Temporada", "Coleccion", "Genero", "SubGrupo", "Familia",
                   "Modelo", "EstiloVida", "Color", "Tela", "Costo"]

        self.view = ProductWindow(self.df_product, headers)
        self.setup_connections()
        self.show()

    def setup_connections(self):
        self.view.search_button.clicked.connect(self.update_selected_products)
        self.view.continue_button.clicked.connect(self.continue_to_next_window)

    def update_selected_products(self):
        query_text = self.view.search_box.text()
        try:
            self.df_product_filtered = self.df_product.query(query_text)
        except Exception as e:
            print(f"Error in query: {e}")
            self.df_product_filtered = self.df_product
        self.view.model.clear()
        self.view.update_selected_products(self.df_product_filtered)

    def continue_to_next_window(self):
        selected_products = self.df_product_filtered["SKU"].tolist()  # Estos productos incluyen todos los agrupadores
        df_selected_product = self.df_product[self.df_product["SKU"].isin(selected_products)].reset_index(drop=True)
        self.close()
        print("Cargando datos")
        self.app_state.set_product_dimensions(df_selected_product)
        self.connection.update_query_products(selected_products)
        self.app_state.set_facts(self.get_facts())
        self.app_state.clean_data()
        self.navigation_controller.phase_1(self.app_state, self.connection)

    def get_facts(self):
        query = "inventories_and_sales"
        return self.connection.execute_query(query)
    
    def show(self):
        self.view.show()

    def close(self):
        self.view.close()
