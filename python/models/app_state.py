import pandas as pd
from datetime import datetime

class AppState:
    def __init__(self):
        self.start_time = datetime.now()
        self.inventory_date = str()
        self.store_dimensions = pd.DataFrame()
        self.product_dimensions = pd.DataFrame()
        self.df_facts = pd.DataFrame()
        self.end_time = None
    
    def set_inventory_date(self, date):
        self.inventory_date = date

    def get_inventory_date(self):
        return self.inventory_date

    def set_store_dimensions(self, data):
        data.loc[data["Capacidad"].isnull(), "Capacidad"]=0
        data.loc[data["Stock"].isnull(), "Stock"]=0
        self.store_dimensions = data.astype({"Capacidad": "int32"}).astype({"Stock": "int32"})

    def get_store_dimensions(self):
        return self.store_dimensions.copy()
    
    def set_product_dimensions(self, data):
        self.product_dimensions = data

    def get_product_dimensions(self):
        return self.product_dimensions.copy()
    
    def set_facts(self, data):
        self.df_facts = data.astype({"CurrentInventory": "int32"}).astype({"AnnualSales": "int32"})

    def get_facts(self):
        return self.df_facts.copy()

    def clean_data(self):
        # 0. Crear variables útiles para el proceso
        stores = self.store_dimensions.loc[self.store_dimensions["Canal"] == "TIENDAS PROPIAS", "CodAlmacen"].tolist()
        wholesales = self.store_dimensions.loc[self.store_dimensions["Canal"] != "TIENDAS PROPIAS", "CodAlmacen"].tolist()
        df = self.df_facts[self.df_facts["CodAlmacen"].isin(stores)
                           ].reset_index().merge(self.product_dimensions[["SKU", "Agrupador"]], on=["SKU"])
        df = df[["CodAlmacen", "Agrupador", "SKU", "CurrentInventory", "AnnualSales"]
                ].sort_values(by=["CodAlmacen", "Agrupador", "SKU"])
        # 1. Eliminar agrupadores sin stock en una copia del DataFrame (Agrupador: SKU sin la diferenciación por talla)
        df_grouper = df.groupby(["Agrupador"], as_index=False).agg({"CurrentInventory": "sum", "AnnualSales": "sum"})
        df_simplified_grouper = df_grouper.loc[df_grouper["CurrentInventory"] != 0]
        # 2. Obtener la lista de agrupadres que se usarán para filtrar
        simplified_list = df_grouper["Agrupador"].tolist()
        # 3. Realizar el filtrado en la copia del DataFrame de hechos con la lista de agrupadores
        df = df.loc[df["Agrupador"].isin(simplified_list)].reset_index(drop=True)
        # 4. Eliminar prendas sin ventas ni stock por cada pareja tienda/agrupador en la copia del DataFrame
        df_store_grouper = df.groupby(["CodAlmacen", "Agrupador"], as_index=False
                                      ).agg({"CurrentInventory": "sum", "AnnualSales": "sum"})
        df_simplified_store_grouper = \
            df_store_grouper.loc[df_store_grouper[["CurrentInventory", "AnnualSales"]].sum(axis=1) !=  0]
        # 5. Se obtienen las tuplas de tiendas/agrupador y almmacén/agrupador que se usará para filtrar el DataFrame de hechos.
        simplified_tuples = list(df_simplified_store_grouper[["CodAlmacen", "Agrupador"]].apply(tuple,axis=1))
        for wholesale in wholesales:
            simplified_tuples += [(wholesale, grouper) for grouper in df_simplified_store_grouper["Agrupador"].unique()]
        # 6. Se realiza el filtrado en el DataFrame de hechos con las tuplas tienda/agrupador.
        self.df_facts = df.loc[df[["CodAlmacen", "Agrupador"]].apply(tuple, axis=1).isin(simplified_tuples)].reset_index(drop=True)

    def setup_kpis(self, df_quarters = None):
        # 1. Inventario actual
        # self.df_facts["CurrentInventory"]
        # 2. Ventas totales del último año
        # self.df_facts["AnnualSales"]
        # 3. Costo total del inventario actual
        unit_cost_dictionary = pd.Series(self.product_dimensions["Costo"].values,
                                         index=self.product_dimensions["SKU"]).to_dict()
        self.df_facts["CurrentInventoryCost"] = \
            self.df_facts["SKU"].map(unit_cost_dictionary).fillna(0)*self.df_facts["CurrentInventory"]
        if df_quarters is not None:
            # 4. Ventas totales del último trimestre
            df_quarters = df_quarters.astype({"QuarterlyPieceSales": "int32"})
            df_quarters.loc[df_quarters["QuarterlyPieceSales"] < 0, "QuarterlyPieceSales"] = 0
            df_quarters["AvgMonthlySalesLastQuarter"] = df_quarters["QuarterlyPieceSales"]/3
            self.df_facts = \
                self.df_facts.merge(df_quarters[["CodAlmacen", "SKU", "AvgMonthlySalesLastQuarter"]], on=["CodAlmacen", "SKU"])
            # 5. Cobertura
            self.df_facts["Coverage"] = self.df_facts["CurrentInventory"]/self.df_facts["AvgMonthlySalesLastQuarter"]

    def finalize(self):
        self.end_time = datetime.now()
