from .connection_manager import ConnectionManager
from .query_manager import QueryManager
import pandas as pd

# Integración de las clases referente a la obtención de datos de la base de datos
# para proporcionar una interfaz centralizada.
class Database:
    def __init__(self) -> None:
        self.connection_manager = ConnectionManager()
        self.query_manager = QueryManager()
        self.query_manager.set_default_queries()
        self.engine = None

    def set_credentials(self, host, database, user, password, port, driver) -> None:
        self.connection_manager.set_credentials(host, database, user, password, port, driver)
    
    def connect(self):
        if self.connection_manager.connect():
            self.engine = self.connection_manager.get_engine()
            return True
        return False

    def execute_query(self, query_key: str):
        query = self.query_manager.get_query(query_key)
        try:
            df = pd.read_sql_query(query, self.engine)
        except Exception as e:
            print(f"Error al obtener datos. {e}")
            df = None
        return df

    def update_query_date(self, date: str) -> None:
        self.query_manager.set_date(date)
        self.query_manager.set_default_queries()

    def update_query_stores(self, stores):
        self.query_manager.set_stores(stores)
        self.query_manager.set_default_queries()

    def update_query_products(self, products):
        self.query_manager.set_products(products)
        self.query_manager.set_default_queries()

    def update_query_store_product(self, store_product_tuples: list) -> None:
        self.query_manager.set_store_product(store_product_tuples)
        self.query_manager.set_default_queries()

    def close(self):
        self.connection_manager.close()
