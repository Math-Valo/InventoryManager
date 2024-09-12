import pandas as pd
import math


class Phase2:
    def __init__(self, df_facts, product_dimensions, df_store_profile) -> None:
        self.df_facts = df_facts
        self.product_dimensions = product_dimensions
        self.store_profile = df_store_profile
        # Información agrupada
        self.grouper_profile = pd.DataFrame({})
        self.store_grouper_profile = pd.DataFrame({})
        # Pivotes
        self.initial_pivot = pd.DataFrame({})
        self.sales_pivot = pd.DataFrame({})
        self.level_pivot = pd.DataFrame({})
        # Parámetros
        self.enough_clothes_stored = 5  # A partir de esta cantidad en almacén, no se mueve nada entre tiendas
        self.maximum_clothing_in_store = 3  # Máxima cantidad de prendas de una talla por tienda
        self.real_maximum_clothing_in_store = 4  # Máxima cantida en caso de que esto haga mejorar la nivelación
        # Cálculo
        self.calculate_leveling()

    def calculate_leveling(self):
        self.setup_dataframes()
        # Cantidad total de bloques (Cantidad de agrupadores distintos en los que dividen los productos)
        total_blocks = self.grouper_profile.shape[0]
        # Nivelar los bloques respecto al costo total de mayor a menor
        for item in range(total_blocks):
            [initial_block, level_block, sales_block] = self.setup_block(item)
            size = self.grouper_profile.loc[self.grouper_profile["Ranking"] == item, "size"].iloc[0]
            if size == 1:
                level_block = self.leveling_blocks_size_one(initial_block, sales_block, level_block)
            else:
                level_block = self.leveling_blocks_size_many(initial_block, sales_block, level_block)
            self.level_pivot.loc[level_block.index, level_block.columns] = level_block.copy()
        # Actualizar DataFrame de hechos por tiendas para agregar los niveles actuales
        self.upgrade_store_profile(first_time=True)
        # Mover productos por agrupador para ajustar a los niveles de la fase 1.
        blocked_stores = self.store_profile[self.store_profile["ToBeModified"] == 0]["CodAlmacen"].tolist()
        MAX_ITER = math.ceil(len(self.store_profile["CodAlmacen"].tolist())/2)
        is_finished = False
        for i in range(MAX_ITER):
            for item in reversed(range(total_blocks)):
                [initial_block, level_block, sales_block] = self.setup_block(item)
                blocked_stores = self.leveling_stores(initial_block, level_block, sales_block, blocked_stores)
            if self.store_profile["ToBeModified"].max() < 50:
                is_finished = True
                break
        if is_finished:
            return None
        for i in range(MAX_ITER):
            for item in reversed(range(total_blocks)):
                [initial_block, level_block, sales_block] = self.setup_block(item)
                blocked_stores = self.leveling_stores(initial_block, level_block, sales_block, blocked_stores,
                                                      activate_stores=True)
            if self.store_profile["ToBeModified"].max() < 50:
                break

    def setup_dataframes(self):
        # Agregar la columna agrupador en una copia de los datos
        df = self.df_facts.merge(self.product_dimensions[["SKU", "Agrupador"]], on=["SKU"])
        # DataFrame agrupado por Agrupador con la suma de los hechos y la cantidad de SKU distintos:
        self.grouper_profile = df.groupby("Agrupador",
                                          as_index=False).agg({"CurrentInventory": "sum",
                                                               "AnnualSales": "sum",
                                                               "CurrentInventoryCost": "sum",
                                                               "AvgMonthlySalesLastQuarter": "sum",
                                                               "SKU": "nunique"}).rename(columns={"SKU": "size"})
        # Agregrar piorización al grouper_profile
        df_grouper_order = self.grouper_profile.sort_values(by=["CurrentInventoryCost", "AnnualSales", "Agrupador"],
                                                            ascending=[False, False, True])
        df_grouper_order["Ranking"] = df_grouper_order.reset_index().index
        self.grouper_profile = self.grouper_profile.merge(df_grouper_order[["Agrupador", "Ranking"]], on=["Agrupador"])
        # DataFrame agrupador por CodAlmacen y Agrupador
        self.initial_pivot = \
            pd.pivot_table(df, values="CurrentInventory", index=["Agrupador", "SKU"], columns=["CodAlmacen"],
                           aggfunc="sum", fill_value=0).reset_index().rename_axis("index", axis=1)
        # Posiblemente, interese dejar solo las TIENDAS PROPIAS
        self.sales_pivot = \
            pd.pivot_table(df, values="AnnualSales", index=["Agrupador", "SKU"], columns=["CodAlmacen"],
                           aggfunc="sum", fill_value=0).reset_index().rename_axis("index", axis=1)
        self.level_pivot = self.initial_pivot.copy()

    def setup_block(self, item):
        grouper = self.grouper_profile.loc[self.grouper_profile["Ranking"] == item, "Agrupador"].iloc[0]
        initial_block = self.initial_pivot[self.initial_pivot["Agrupador"] == grouper].copy()
        level_block = self.level_pivot[self.level_pivot["Agrupador"] == grouper].copy()
        sales_block = self.sales_pivot[self.sales_pivot["Agrupador"] == grouper].copy()
        return [initial_block, level_block, sales_block]

    def leveling_blocks_size_one(self, initial, sales, level):
        # CONSTANTES:
        # Se requiere tener la lista de tiendas a analizar; es decir, sin almacenes.
        stores = self.store_profile["CodAlmacen"].tolist()
        # Conocer el inventario total
        total_inventory = initial[stores].sum(axis=1).sum()
        # Y conocer las ventas totales de las prendas
        # Pero si no hay ventas por prenda, usar las ventas totales de la tienda
        total_sales = sales[stores].sum(axis=1).sum()
        if total_sales == 0:
            total_sales = self.store_profile["AnnualSales"].sum()
            for store in stores:
                sales.iloc[0, sales.columns.get_loc(store)] = \
                    self.store_profile[self.store_profile["CodAlmacen"] == store]["AnnualSales"].iloc[0]
        # Recalcular el límite máximo por tallas
        maximum_clothing_in_store = max(self.maximum_clothing_in_store, math.ceil(total_sales / len(stores)))

        # No hacer nada si en almacenes hay bastante ropa
        if self.enough_clothes_in_wholesales(initial, stores):
            return level

        # NIVELACIÓN
        # Se distribuye el inventario total en proporción a las ventas en la tienda con respecto a las ventas totales
        for store in stores:
            level.iloc[0, level.columns.get_loc(store)] = \
                min(maximum_clothing_in_store,
                    math.ceil(total_inventory*sales.iloc[0, sales.columns.get_loc(store)]/total_sales))
        # Se analiza el ajuste que hay que hacer
        difference = total_inventory - level[stores].sum(axis=1).sum()
        if difference == 0:
            return level
        # Si hay que agregar o quitar inventario, se tendrá que hacer a partir de las ventas en tienda.
        # Comenzando por considerar las ventas de la prenda actual o, si no hay ventas, de las ventas totales.
        unpivot_sales = pd.melt(sales, id_vars=["SKU"], value_vars=stores, var_name="CodAlmacen",
                                value_name="AnnualSales")
        # Ordenar las tiendas en orden ascendente respecto de sus ventas en la talla dada.
        # O si no hay ventas de la talla, en orden ascendente respecto de sus ventas totales.
        if unpivot_sales["AnnualSales"].sum() != 0:
            stores_sorted_by_sales = unpivot_sales.sort_values(by=["AnnualSales"])["CodAlmacen"].tolist()
        else:
            stores_sorted_by_sales = self.store_profile.sort_values(by=["AnnualSales"])["CodAlmacen"].tolist()
        if difference < 0:
            for store in stores_sorted_by_sales:
                while difference < 0 < level[store].sum():
                    level.iloc[0, level.columns.get_loc(store)] -= 1
                    difference += 1
                if difference == 0:
                    return level
        if difference > 0:
            stores_with_sales = [store for store in stores_sorted_by_sales if sales[store].sum() >= 0]
            stores_without_sales = [store for store in stores_sorted_by_sales if store not in stores_with_sales]
            stores_without_sales_sorted = self.store_profile[self.store_profile["CodAlmacen"].isin(stores_without_sales)
                                                             ].sort_values(by=["AnnualSales"])["CodAlmacen"].tolist()
            for store in reversed(stores_sorted_by_sales):
                if store in stores_without_sales:
                    break
                while level.iloc[0, level.columns.get_loc(store)] < maximum_clothing_in_store and difference > 0:
                    level.iloc[0, level.columns.get_loc(store)] += 1
                    difference -= 1
                if difference == 0:
                    return level
            for store in reversed(stores_without_sales_sorted):
                while level.iloc[0, level.columns.get_loc(store)] < maximum_clothing_in_store and difference > 0:
                    level.iloc[0, level.columns.get_loc(store)] += 1
                    difference -= 1
                if difference == 0:
                    break
        return level

    def leveling_blocks_size_many(self, initial, sales, level):
        # CONSTANTE
        # Se requiere tener una lista de las tiendas a analizar
        stores = self.store_profile["CodAlmacen"].tolist()
        # La cantidad mínima de tiendas activas depende de la máxima distribución de la talla con más inventario
        minimum_active_stores = 1
        # La cantidad máxima de tiendas que se pueden tallar por completo depende de la talla con menos inventario
        maximum_stores_fully_sized = len(stores)

        # TEST INICIAL
        # No hacer nada si en los almacenes hay bastante ropa
        if self.enough_clothes_in_wholesales(initial, stores):
            return level

        # Conocer el inventario total por talla
        total_inventory_per_sku = pd.melt(initial[["Agrupador", "SKU"]+stores], id_vars=["SKU"],
                                          value_vars=stores, value_name="CurrentInventory"
                                          ).groupby(["SKU"], as_index=False
                                                    ).agg({"CurrentInventory": "sum"})
        # Conocer el inventario total por tienda (no tiene uso)
        # total_inventory_per_store = pd.melt(initial[["Agrupador"]+stores].groupby(["Agrupador"],
        #                                                                           as_index=False).sum(),
        #                                     id_vars=["Agrupador"], value_vars=stores,
        #                                     var_name="CodAlmacen", value_name="CurrentInventory")
        # Conocer el inventario total (No tiene uso)
        # total_inventory = int(initial[stores].sum(axis=1).sum())
        # Conocer las ventas totales por talla
        total_sales_per_sku = pd.melt(sales, id_vars=["SKU"], value_vars=stores, value_name="AnnualSales"
                                      )[["SKU", "AnnualSales"]].groupby(["SKU"], as_index=False).sum()
        # Conocer las ventas totales por tiendas
        total_sales_per_store = pd.melt(sales[["Agrupador"]+stores].groupby(["Agrupador"], as_index=False).sum(),
                                        id_vars=["Agrupador"], value_vars=stores,
                                        var_name="CodAlmacen", value_name="AnnualSales")
        # Conocer las ventas totales
        total_sales = int(sales[stores].sum(axis=1).sum())

        # Se va a hacer la nivelación en proporción a las ventas por tiendas, por lo que se requiere que haya ventas
        exists_sales_per_store = total_sales != 0

        # La siguiente lista ayudará a priorizar, basándose de las ventas en tienda.
        # Comenzando por considerar las ventas de la prenda actual o, si no hay ventas, de las ventas totales.
        if total_sales_per_store["AnnualSales"].sum() != 0:
            stores_sorted_by_sales = total_sales_per_store.sort_values(by=["AnnualSales"])["CodAlmacen"].tolist()
        else:
            stores_sorted_by_sales = self.store_profile.sort_values(by=["AnnualSales"])["CodAlmacen"].tolist()

        if not exists_sales_per_store:
            # En caso de que no haya ventas, se usarán las ventas totales por tienda.
            total_sales = self.store_profile["AnnualSales"].sum()
            total_sales_per_store = sales[["Agrupador"] + stores].head(1).copy()
            for store in stores:
                total_sales_per_store.iloc[0, total_sales_per_store.columns.get_loc(store)] = \
                    self.store_profile[self.store_profile["CodAlmacen"] == store]["AnnualSales"].sum()

        # NIVELACIÓN

        # INICIALIZACIÓN
        # Se distribuye el inventario para cada SKU individualmente del mismo modo que en los bloques de uno:
        # Se distribuye en proporción a las ventas en la tienda respecto a las ventas totales por el inventario total
        index = 0
        for sku in total_inventory_per_sku["SKU"].tolist():
            # Recalcular el límite máximo de tallas por tienda.
            maximum_clothing_in_store = max(self.maximum_clothing_in_store,
                                            math.ceil(total_inventory_per_sku[total_inventory_per_sku["SKU"] == sku
                                                                              ].reset_index().loc[0, "CurrentInventory"]
                                                      / len(stores)))
            minimum_active_stores = max(minimum_active_stores,
                                        math.ceil(total_inventory_per_sku.iloc[index, 1] / maximum_clothing_in_store))
            maximum_stores_fully_sized = min(maximum_stores_fully_sized,
                                             int(total_inventory_per_sku.iloc[index, 1]))

            for store in stores:  # Hay una forma más fácil de hacer esto, usando apply(), pero estoy cansado. :(
                # Se realiza el cálculo
                level.iloc[index, level.columns.get_loc(store)] = \
                    min(maximum_clothing_in_store,
                        math.ceil(total_inventory_per_sku[total_inventory_per_sku["SKU"] == sku
                                                          ].reset_index().loc[0, "CurrentInventory"]
                                  * total_sales_per_store[total_sales_per_store["CodAlmacen"] == store
                                                          ].reset_index().loc[0, "AnnualSales"]
                                  / total_sales))

            # Se calcula la diferencia del inventario por sku
            difference = int(total_inventory_per_sku[total_inventory_per_sku["SKU"] == sku
                                                     ].reset_index().loc[0, "CurrentInventory"]) - \
                int(level[level["SKU"] == sku][stores].sum(axis=1).iloc[0])
            if difference == 0:
                index += 1
                continue

            # Ahora sí, a hacer los ajustes
            if difference < 0:
                for store in stores_sorted_by_sales:
                    while difference < 0 < level[level["SKU"] == sku].iloc[0, level.columns.get_loc(store)]:
                        level.iloc[index, level.columns.get_loc(store)] -= 1
                        difference += 1
                    if difference == 0:
                        break
            else:
                stores_with_sales = [store for store in stores_sorted_by_sales
                                     if int(total_sales_per_store[total_sales_per_store["CodAlmacen"] == store
                                                                  ].reset_index(drop=True).iloc[0, 2]) != 0]
                stores_without_sales = [store for store in stores_sorted_by_sales if store not in stores_with_sales]
                stores_without_sales_sorted = \
                    self.store_profile[self.store_profile["CodAlmacen"].isin(stores_without_sales)
                                       ].sort_values(by=["AnnualSales"])["CodAlmacen"].tolist()
                for store in reversed(stores_sorted_by_sales):
                    if store in stores_without_sales:
                        break
                    while level[level["SKU"] == sku].iloc[0, level.columns.get_loc(store)] < maximum_clothing_in_store \
                            and difference > 0:
                        level.iloc[index, level.columns.get_loc(store)] += 1
                        difference -= 1
                    if difference == 0:
                        break
                for store in reversed(stores_without_sales_sorted):
                    while level[level["SKU"] == sku].iloc[0, level.columns.get_loc(store)] < maximum_clothing_in_store \
                            and difference > 0:
                        level.iloc[index, level.columns.get_loc(store)] += 1
                        difference -= 1
                    if difference == 0:
                        break
            index += 1

        # TALLADO
        # Total de tiendas activas en este momento
        total_active_stores = len(level[stores].columns[level[stores].sum() > 0])

        if minimum_active_stores <= maximum_stores_fully_sized:  # Se pueden tallar todas las tiendas
            if maximum_stores_fully_sized < total_active_stores:
                for bad_store in stores_sorted_by_sales:
                    if level[bad_store].sum() == 0:
                        continue
                    index = 0
                    for sku in total_inventory_per_sku["SKU"].tolist():
                        inventory_in_bad_store = level[level["SKU"] == sku].iloc[0, level.columns.get_loc(bad_store)]
                        if inventory_in_bad_store == 0:
                            index += 1
                            continue
                        maximum_clothing_in_store = max(self.maximum_clothing_in_store,
                                                        math.ceil(total_inventory_per_sku[
                                                                      total_inventory_per_sku["SKU"] == sku
                                                                      ].reset_index().loc[0, "CurrentInventory"]
                                                                  / len(stores)))
                        for good_store in reversed(stores_sorted_by_sales):
                            inventory_in_good_store = \
                                level[level["SKU"] == sku].iloc[0, level.columns.get_loc(good_store)]
                            if inventory_in_good_store < maximum_clothing_in_store:
                                move = min(maximum_clothing_in_store - inventory_in_good_store,
                                           inventory_in_bad_store)
                                level.iloc[index, level.columns.get_loc(good_store)] += move
                                level.iloc[index, level.columns.get_loc(bad_store)] -= move
                                inventory_in_bad_store -= move
                            if inventory_in_bad_store == 0:
                                break
                        index += 1
                    total_active_stores -= 1
                    if maximum_stores_fully_sized == total_active_stores:
                        break
            # Tenemos a lo más el máximo de tiendas en uso y queda asegurarse de que no haya ceros...
            no_empty_stores = [store for store in stores if level[store].sum() > 0]
            empty_sku = total_inventory_per_sku[total_inventory_per_sku["CurrentInventory"] == 0]["SKU"].tolist()
            for store in reversed(stores_sorted_by_sales[-total_active_stores:]):
                if store not in no_empty_stores:
                    continue
                if level[~level["SKU"].isin(empty_sku)][store].min() > 0:
                    continue
                index = 0
                for sku in total_inventory_per_sku["SKU"].tolist():
                    if sku in empty_sku:
                        index += 1
                        continue
                    if level.iloc[index, level.columns.get_loc(store)] > 0:
                        index += 1
                        continue
                    for sender_store in stores_sorted_by_sales[-total_active_stores:]:
                        if sender_store == store:
                            continue
                        if level[level["SKU"] == sku].reset_index(drop=True).\
                                iloc[0, level.columns.get_loc(sender_store)] > 1:
                            level.iloc[index, level.columns.get_loc(sender_store)] -= 1
                            level.iloc[index, level.columns.get_loc(store)] += 1
                            break
                    index += 1
        else:  # Debido a inventario insuficiente, no todas las tiendas estarán totalmente talladas
            # Distribuimos las piezas de los SKU con más inventario para tener la mínima cantidad de tiendas activas
            upper_inventory = total_inventory_per_sku["CurrentInventory"].max()
            upper_maximum_clothing_in_store = max(self.maximum_clothing_in_store,
                                                  math.ceil(upper_inventory/len(stores)))
            skus_with_upper_inventory = total_inventory_per_sku[total_inventory_per_sku["CurrentInventory"] /
                                                                upper_maximum_clothing_in_store >
                                                                minimum_active_stores - 1]["SKU"].tolist()
            index = 0
            for sku in total_inventory_per_sku["SKU"].tolist():
                if sku not in skus_with_upper_inventory:
                    index += 1
                    continue
                current_inventory = int(total_inventory_per_sku.iloc[index, 1])
                for store in reversed(stores_sorted_by_sales):
                    if current_inventory > 0:
                        move = min(upper_maximum_clothing_in_store, current_inventory)
                        level.iloc[index, level.columns.get_loc(store)] = move
                        current_inventory -= move
                    else:
                        level.iloc[index, level.columns.get_loc(store)] = 0
                index += 1
            # Distribuimos las piezas de los SKU con menos inventario del mínimo de tiendas activas
            # para tener la máxima cantidad de tiendas talladas o al menos no vacías
            # lower_inventory = total_inventory_per_store["CurrentInventory"].min()
            skus_with_lower_inventory = total_inventory_per_sku[total_inventory_per_sku["CurrentInventory"] <
                                                                minimum_active_stores]["SKU"].tolist()
            index = 0
            for sku in total_inventory_per_sku["SKU"].tolist():
                if sku not in skus_with_lower_inventory:
                    index += 1
                    continue
                current_inventory = int(total_inventory_per_sku.iloc[index, 1])
                for store in reversed(stores_sorted_by_sales):
                    if current_inventory > 0:
                        level.iloc[index, level.columns.get_loc(store)] = 1
                        current_inventory -= 1
                    else:
                        level.iloc[index, level.columns.get_loc(store)] = 0
                index += 1
            # Distribuimos las piezas de los SKU que pueden estar en todas las tiendas
            skus_remaining = total_inventory_per_sku[~total_sales_per_sku["SKU"].isin(skus_with_lower_inventory +
                                                                                      skus_with_upper_inventory)
                                                     ]["SKU"].tolist()
            index = 0
            for sku in total_inventory_per_sku["SKU"].tolist():
                if sku not in skus_remaining:
                    index += 1
                    continue
                current_inventory = int(total_inventory_per_sku.iloc[index, 1])
                for store in stores:
                    level.iloc[index, level.columns.get_loc(store)] = 0
                while current_inventory > 0:
                    for store in reversed(stores_sorted_by_sales[-minimum_active_stores:]):
                        if current_inventory == 0:
                            break
                        level.iloc[index, level.columns.get_loc(store)] += 1
                        current_inventory -= 1
                index += 1
        return level

    def enough_clothes_in_wholesales(self, initial, stores) -> bool:
        inventory_in_wholesales = initial[initial.columns.difference(["index", "Agrupador", "SKU"] + stores)]
        test = inventory_in_wholesales.sum(axis=1).max() > len(stores)/2 or \
            inventory_in_wholesales.sum(axis=1).sum() > self.enough_clothes_stored
        return test

    def upgrade_store_profile(self, first_time=False):
        if not first_time:
            del self.store_profile["LeveledInventory"]
        stores = self.store_profile["CodAlmacen"].tolist()
        df_with_leveled_inventory = pd.DataFrame({"CodAlmacen": stores,
                                                  "LeveledInventory": (self.level_pivot[stores].sum()).tolist()})
        self.store_profile = self.store_profile.merge(df_with_leveled_inventory, on="CodAlmacen")
        self.store_profile["FinalLevel"] = (self.store_profile["LeveledInventory"] -
                                            self.store_profile["CurrentInventory"])
        self.store_profile["ToBeModified"] = self.store_profile["ExpectedLevel"] - self.store_profile["FinalLevel"]

    def leveling_stores(self, initial, level, sales, blocked, fill_empty_stores=True, activate_stores=False):
        [require_more, require_less] = self.update_leveling_requirements(blocked)
        stores = require_more + require_less
        if activate_stores:
            # Si se van a activar tiendas nuevas, entonces todas las tiendas son válidas para mover producto.
            historic_stores = stores
        else:
            # Si no, se requiere conocer las tiendas que alguna vez han tenido producto
            historic_stores = [store for store in stores if initial[store].sum() > 0 or sales[store].sum()]
        # Los movimientos se priorizarán para que afecte lo menos posible al costo potencial.
        # Es decir, se moverá en orden de los agrupadores de menor costo de inventario a los de mayor costo.
        transmitting_stores = [store for store in require_less if level[store].sum() > 0]
        if self.enough_clothes_in_wholesales(initial, self.store_profile["CodAlmacen"].tolist()):
            return blocked
        if len(transmitting_stores) == 0:
            return blocked
        if fill_empty_stores:
            receiving_stores = [store for store in require_more if level[store].sum() == 0 and store in historic_stores]
        else:
            receiving_stores = [store for store in require_more
                                if level[store].max().max() < self.maximum_clothing_in_store]
        if len(receiving_stores) == 0:
            return blocked
        # Crear la lista de tiendas ordenadas por ventas
        # total_sales_per_store = pd.melt(sales[["Agrupador"]+stores].groupby(["Agrupador"], as_index=False).sum(),
        #                                 id_vars=["Agrupador"], value_vars=stores,
        #                                 var_name="CodAlmacen", value_name="AnnualSales")
        # if total_sales_per_store["AnnualSales"].sum() != 0:
        #     stores_sorted_by_sales = total_sales_per_store.sort_values(by=["AnnualSales"])["CodAlmacen"].tolist()
        # else:
        #     stores_sorted_by_sales = self.store_profile.sort_values(by=["AnnualSales"])["CodAlmacen"].tolist()
        products = initial["SKU"].tolist()
        for transmitting_store in transmitting_stores:
            for receiving_store in receiving_stores:
                if level[receiving_store].sum() > 0:  # Al principio no sucede esto, pero eventualmente puede ocurrir.
                    continue
                index = 0
                for sku in products:
                    move = int(level[level["SKU"] == sku][transmitting_store].iloc[0])
                    level.iloc[index, level.columns.get_loc(receiving_store)] = move
                    level.iloc[index, level.columns.get_loc(transmitting_store)] = 0
                    index += 1
                break
        self.level_pivot.loc[level.index, level.columns] = level.copy()
        [new_require_more, new_require_less] = self.update_leveling_requirements(blocked, recalculate=True)
        blocked += [store for store in require_more if store not in new_require_more]
        blocked += [store for store in require_less if store not in new_require_less]
        return blocked

    def update_leveling_requirements(self, blocked, recalculate=False):
        if recalculate:
            self.upgrade_store_profile()
        # Ordenar (ascendentemente) las tiendas según la cantidad de movimientos que haya que hacer
        stores_sorted_by_modifications = self.store_profile[["CodAlmacen", "ToBeModified"]
                                                            ].sort_values(by=["ToBeModified"])
        # Las tiendas que deben de tener más inventario
        stores_that_require_more = stores_sorted_by_modifications[stores_sorted_by_modifications["ToBeModified"] > 0
                                                                  ]["CodAlmacen"].tolist()
        # Las tiendas que deben de tener menos inventario
        stores_that_require_less = stores_sorted_by_modifications[stores_sorted_by_modifications["ToBeModified"] < 0
                                                                  ]["CodAlmacen"].tolist()[::-1]
        # Quitar las tiendas que ya fueron bloqueadas por procesos anteriores
        final_stores_that_require_more = [store for store in stores_that_require_more if store not in blocked]
        final_stores_that_require_less = [store for store in stores_that_require_less if store not in blocked]
        return [final_stores_that_require_more, final_stores_that_require_less]

    def clean(self):
        stores = self.store_profile["CodAlmacen"].tolist()
        zero_inventory_sku_list = self.initial_pivot[self.initial_pivot[stores].sum(axis=1) == 0]["SKU"].tolist()
        self.initial_pivot =\
            self.initial_pivot[~self.initial_pivot["SKU"].isin(zero_inventory_sku_list)].reset_index(drop=True)
        self.level_pivot =\
            self.level_pivot[~self.level_pivot["SKU"].isin(zero_inventory_sku_list)].reset_index(drop=True)
        self.sales_pivot =\
            self.sales_pivot[~self.sales_pivot["SKU"].isin(zero_inventory_sku_list)].reset_index(drop=True)