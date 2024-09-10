import pandas as pd


class Phase3:
    def __init__(self, initial_pivot, level_pivot, store_profile, store_dimension):
        self.initial = initial_pivot
        self.level = level_pivot
        self.store_profile = store_profile
        # DataFrames de movimientos
        self.shipping_movements = self.level[["Agrupador", "SKU"]].copy()
        self.receipt_movements = self.shipping_movements.copy()
        # listas para crear las columnas del DataFrame de envíos
        self.shipping_store = list()
        self.receipt_store = list()
        self.product = list()
        self.shipping = list()
        # Recursos que se usarán a lo largo del cálculo
        self.stores = self.store_profile["CodAlmacen"].tolist()
        self.total_sku = self.initial.shape[0]
        self.shipping_stores_sorted = self.store_profile[["CodAlmacen"]].copy()
        self.receipt_stores_sorted = store_dimension[store_dimension["CodAlmacen"].isin(self.stores)
                                                     ][["CodAlmacen", "Ciudad", "Estado", "Region"]]
        # Obtener el DataFrame resultante
        self.calculate_data_frame_fields()
        self.shipments = pd.DataFrame({"sending": self.shipping_store, "receiving": self.receipt_store,
                                       "sku": self.product, "shipping": self.shipping}).\
            sort_values(by=["sending", "sku", "receiving"])

    def calculate_movements(self):
        movements = self.level[self.stores] - self.initial[self.stores]
        self.shipping_movements[self.stores] = movements[self.stores].mask(movements[self.stores] > 0, 0)
        self.receipt_movements[self.stores] = movements[self.stores] - self.shipping_movements[self.stores]

    def calculate_priority(self):
        # El registro de movimientos se inicializa decidiendo la tienda que enviará producto
        # y la prioridad de envíos es desde la tienda que más debe de enviar.
        shipping_movements_by_stores = self.shipping_movements[self.stores].sum()
        self.shipping_stores_sorted["shipping"] =\
            self.shipping_stores_sorted.apply(lambda x: shipping_movements_by_stores[x["CodAlmacen"]], axis=1)
        stores_prioritized = self.shipping_stores_sorted.sort_values(by=["shipping"])
        stores_prioritized["Ranking"] = stores_prioritized.reset_index().index
        self.shipping_stores_sorted =\
            self.shipping_stores_sorted.merge(stores_prioritized[["CodAlmacen", "Ranking"]], on="CodAlmacen")

        # Luego entonces, se elige a la tienda que va a recibir el producto
        # y la prioridad de recepción es con las tiendas más cercadas,
        # priorizando la ciudad más cercana, luego el estado y luego la región.
        # En casos de empate, se priorizará aquellas tiendas que necesiten recibir más.
        receipt_movements_by_stores = self.receipt_movements[self.stores].sum()
        self.receipt_stores_sorted["receipt"] =\
            self.receipt_stores_sorted.apply(lambda x: receipt_movements_by_stores[x["CodAlmacen"]], axis=1)
        stores_prioritized = self.receipt_stores_sorted.sort_values(by=["Ciudad", "Estado", "Region", "receipt"],
                                                                    ascending=[True, True, True, False])
        stores_prioritized["Ranking"] = stores_prioritized.reset_index().index
        self.receipt_stores_sorted =\
            self.receipt_stores_sorted.merge(stores_prioritized[["CodAlmacen", "Ranking"]], on="CodAlmacen")

    def calculate_data_frame_fields(self):
        # Establecer valores
        self.calculate_movements()
        self.calculate_priority()

        # Calcular los campos para el DataFrame de movimientos
        for shipping_place in range(len(self.stores)):
            shipping_store = self.shipping_stores_sorted.loc[self.shipping_stores_sorted["Ranking"] == shipping_place,
                                                             "CodAlmacen"].iloc[0]
            if self.shipping_stores_sorted.loc[self.shipping_stores_sorted["CodAlmacen"] == shipping_store,
                                               "shipping"].iloc[0] == 0:
                continue
            for sku in range(self.total_sku):
                shipping_available =\
                    -int(self.shipping_movements.iloc[sku, self.shipping_movements.columns.get_loc(shipping_store)])
                if shipping_available == 0:
                    continue
                for receipt_place in range(len(self.stores)):
                    receipt_store = self.receipt_stores_sorted.loc[self.receipt_stores_sorted["Ranking"] ==
                                                                   receipt_place, "CodAlmacen"].iloc[0]
                    receipt_available =\
                        int(self.receipt_movements.iloc[sku, self.receipt_movements.columns.get_loc(receipt_store)])
                    if shipping_store == receipt_store or receipt_available == 0:
                        continue
                    move = min(shipping_available, receipt_available)
                    self.shipping_store.append(shipping_store)
                    self.receipt_store.append(receipt_store)
                    self.product.append(self.initial.iloc[sku, self.initial.columns.get_loc("SKU")])
                    self.shipping.append(move)
                    self.shipping_movements.iloc[sku, self.shipping_movements.columns.get_loc(shipping_store)] += move
                    self.receipt_movements.iloc[sku, self.receipt_movements.columns.get_loc(receipt_store)] -= move
