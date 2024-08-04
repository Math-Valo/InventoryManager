from views.product_window import ProductWindow


class ProductController:
    def __init__(self, navigation_controller, settings, database_connection, app_state) -> None:
        self.navigation_controller = navigation_controller
        self.settings = settings
        self.app_state = app_state
        self.connection = database_connection

        self.df_product = self.app_state.get_product_dimensions()
        self.df_product_filtered = self.df_product
        self.view = ProductWindow(self.df_product)
        self.setup_connections()
        self.show()

    def setup_connections(self):
        self.view.search_button.clicked.connect(self.update_selected_products)
        self.view.continue_button.clicked.connect(self.continue_to_next_window)

    def update_selected_products(self):
        headers = ["SKU", "Temporada", "Coleccion", "Genero", "SubGrupo", "Familia",
                   "Modelo", "EstiloVida", "Color", "Tela", "Costo"]
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
        print("Fase_1: Determinación de los niveles por tiendas")
        df_facts = self.app_state.get_facts()
        store_product_tuples = df_facts[["CodAlmacen", "SKU"]].apply(tuple, axis=1).tolist()
        self.connection.update_query_store_product(store_product_tuples)
        self.app_state.setup_kpis(self.get_quarters())
        

        from models.phase_1 import Phase1
        levels = Phase1(self.app_state.get_store_dimensions(),
                       self.app_state.get_facts())
        print(levels.store_profile)
        self.navigation_controller.phase_1(self.app_state, self.connection)

    def get_facts(self):
        query = "inventories_and_sales"
        return self.connection.execute_query(query)
    
    def get_quarters(self):
        query = "quarter_sales"
        return self.connection.execute_query(query)

    def show(self):
        self.view.show()

    def close(self):
        self.view.close()
