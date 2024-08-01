import pandas as pd
from datetime import datetime

class AppState:
    def __init__(self):
        self.inventory_date = str()
        self.inventory_data = pd.DataFrame()
        self.filtered_inventory_data = pd.DataFrame()
        self.sales_data = pd.DataFrame()
        self.store_dimensions = pd.DataFrame()
        self.product_dimensions = pd.DataFrame()
        self.start_time = datetime.now()
        self.end_time = None
    
    def set_inventory_date(self, date):
        self.inventory_date = date

    def get_inventory_date(self):
        return self.inventory_date
    
    def set_inventory_data(self, data):
        self.inventory_data = data
        self.filtered_inventory_data = data

    def filter_stores(self, store_codes):
        self.filtered_inventory_data = self.filtered_inventory_data[self.filtered_inventory_data['store_code'].isin(store_codes)]
    
    def filter_products(self, product_codes):
        self.filtered_inventory_data = self.filtered_inventory_data[self.filtered_inventory_data['product_code'].isin(product_codes)]
    
    def set_sales_data(self, data):
        self.sales_data = data
    
    def set_store_dimensions(self, data):
        data.loc[data["Capacidad"].isnull(), "Capacidad"]=0
        data.loc[data["Stock"].isnull(), "Stock"]=0
        self.store_dimensions = data.astype({"Capacidad": "int32"}).astype({"Stock": "int32"})

    def get_store_dimensions(self):
        return self.store_dimensions
    
    def set_product_dimensions(self, data):
        self.product_dimensions = data

    def get_product_dimensions(self):
        return self.product_dimensions
    
    def finalize(self):
        self.end_time = datetime.now()
