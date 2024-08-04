import pandas as pd
import numpy as np
import math
import sys


class Phase1:
    def __init__(self, df_store, df_facts) -> None:
        # DataFrames
        self.df_store = df_store
        self.df_facts = df_facts
        self.store_profile = pd.DataFrame({})
        # Límites respecto a la cobertura (se puede ignorar si es imposible respetar)
        self.minimum_acceptable_coverage = 2.5
        self.maximum_acceptable_coverage = 4
        # Límites respecto al porcentaje de la capacidad de la tienda
        self.minimum_capacity_percentage = 0.8
        self.maximum_capacity_percentage = 1.2
        # Límite de prendas que se puede poner o quitar en una tienda
        self.maximum_movement_to_add = 100
        self.maximum_movement_to_remove = -100
        # Límites inferior y superior para el rango del nivel respecto al esperado
        self.range_lower_limite = -50
        self.range_upper_limite = 50
        # Intentos máximos para calcular los niveles
        self.max_executions = 50
        self.calculate_levels()

    def calculate_levels(self):
        self.load_information_by_store()
        self.store_profile["ExpectedLevel"] = \
            self.store_profile.apply(lambda x: self.initial_inventory_level(x["Special"],
                                                                            x["Available"],
                                                                            x["Coverage"],
                                                                            x["CoverageClassification"],
                                                                            x["AvgMonthlySalesLastQuarter"],
                                                                            x["Capacidad"]), axis=1)
        execution = 0
        while execution <= self.max_executions and not self.feasibility_test():
            movement = self.store_profile["ExpectedLevel"].sum()
            if movement < 0:  # Estamos quitando de más
                # Se aumentará a las tiendas que más venden
                for item in range(self.store_profile.shape[0]):
                    # Esto funciona porque es prácticamente imposible tener exactamente la misma cantidad de ventas en 2 tiendas
                    level = self.store_profile.loc[self.store_profile["SortingSales"] == item+1,
                                                   "ExpectedLevel"].iloc[0]
                    capacity = self.store_profile.loc[self.store_profile["SortingSales"] == item+1,
                                                      "Capacidad"].iloc[0]
                    available = self.store_profile.loc[self.store_profile["SortingSales"] == item+1,
                                                       "Available"].iloc[0]
                    average_sale = self.store_profile.loc[self.store_profile["SortingSales"] == item+1,
                                                          "AvgMonthlySalesLastQuarter"].iloc[0]
                    # ¿Se le puede agregar prendas a la tienda?
                    while self.adding_level_test(level, capacity, available, average_sale) and movement < 0:
                        movement += 1
                        self.store_profile.loc[self.store_profile["SortingSales"] == item+1, "ExpectedLevel"] += 1
                        level += 1
                if movement < 0:  # Es posible que aún repasando todas las tiendas aún no se cumplan los requisitos
                    # El mayor problema por el cual pasa esto es por respetar los límites de la cobertura. Vamos a ignorarlo.
                    for item in range(self.store_profile.shape[0]):
                        level = self.store_profile.loc[self.store_profile["SortingSales"] == item+1,
                                                       "ExpectedLevel"].iloc[0]
                        capacity = self.store_profile.loc[self.store_profile["SortingSales"] == item+1,
                                                          "Capacidad"].iloc[0]
                        available = self.store_profile.loc[self.store_profile["SortingSales"] == item+1,
                                                           "Available"].iloc[0]
                        average_sale = self.store_profile.loc[self.store_profile["SortingSales"] == item+1,
                                                              "AvgMonthlySalesLastQuarter"].iloc[0]
                        while self.adding_level_test(level, capacity, available, average_sale, is_covered=False) and movement < 0:
                            movement += 1
                            self.store_profile.loc[self.store_profile["SortingSales"] == item+1, "ExpectedLevel"] += 1
                            level += 1
                    # A continuación: avisar al usuario de los temas encontrados:
                    if movement < 0:
                        # Si ya aumentamos tood lo posible a cada tienda y aún se necesita aumentar, seguro es un tema de capacidades
                        print("Capacidades insuficientes para satisfacer las necesidades. Aumentar capacidades en las tiendas")
                        sys.exit()
                    else:
                        # De cualquier forma, llegar acá implica que se ignoró las cobertura y se avisará al usuario de ello
                        print("Hay temas de cobertura que convendría que se examinen")
            else:  # Estamos agregando prendas de más
                # Se disminuirá a las tiendas que menos venden
                total_stores = self.store_profile.shape[0]
                for item in range(self.store_profile.shape[0]):
                    level = self.store_profile.loc[self.store_profile["SortingSales"] == total_stores - item,
                                                   "ExpectedLevel"].iloc[0]
                    capacity = self.store_profile.loc[self.store_profile["SortingSales"] == total_stores - item,
                                                      "Capacidad"].iloc[0]
                    available = self.store_profile.loc[self.store_profile["SortingSales"] == total_stores - item,
                                                       "Available"].iloc[0]
                    average_sale = self.store_profile.loc[self.store_profile["SortingSales"] == total_stores - item,
                                                          "AvgMonthlySalesLastQuarter"].iloc[0]
                    fashion_stock = self.store_profile.loc[self.store_profile["SortingSales"] == total_stores - item,
                                                           "CurrentInventory"].iloc[0]
                    # ¿Se le puede quitar prendas a la tienda?
                    while self.removing_level_test(level, capacity, available, average_sale, fashion_stock) and movement > 0:
                        movement -= 1
                        self.store_profile.loc[self.store_profile["SortingSales"] == total_stores - item,
                                               "ExpectedLevel"] -= 1
                        level -= 1
                if movement < 0:
                    # Si ya disminuimos todo lo posible a cada tienda y aún se necesita quitar, entonces hay un problema de capacidades
                    print("Capacidades subestimadas estimadas para satisfacer las necesidades. Disminuir capacidades en las tiendas")
                    sys.exit()
            execution += 1
        if self.feasibility_test():
            print("Niveles ajustados adecuadamente")
        else:
            print("No se pudieron ajustar adecuadamente los niveles. Favor de revisar los parámetros")
            # sys.exit()

        # Con los niveles esperados, queda calcular los rangos inferiores y superiores
        # De momento no hay un criterio mayor para los límites inferior y superior
        self.store_profile["MinimumLevel"] = \
            self.store_profile.apply(lambda x: max(x["ExpectedLevel"] + self.range_lower_limite,
                                                   self.maximum_movement_to_remove), axis=1)
        self.store_profile["MaximumLevel"] = \
            self.store_profile.apply(lambda x: max(x["ExpectedLevel"] + self.range_upper_limite,
                                                   self.maximum_movement_to_add), axis=1)

    def load_information_by_store(self):
        # Variables útiles
        special_stores = self.df_store.loc[(self.df_store["Canal"] == "TIENDAS PROPIAS") &
                                           (self.df_store["Zona"] == "AEROPUERTO"), "CodAlmacen"].tolist()
        store_columns = ["CodAlmacen", "NombreAlmacen", "Capacidad", "Stock"]
        df_store_facts = \
            self.df_facts[["CodAlmacen", "CurrentInventory", "AvgMonthlySalesLastQuarter",
                           "AnnualSales"]].groupby(["CodAlmacen"],
                                                   as_index=False).agg({"CurrentInventory": "sum",
                                                                        "AvgMonthlySalesLastQuarter": "sum",
                                                                        "AnnualSales": "sum"})
        # Inicializar DataFrame
        self.store_profile = self.df_store[store_columns].merge(df_store_facts, on=["CodAlmacen"])
        # Indicadores
        self.store_profile["Available"] = self.store_profile["Capacidad"] - self.store_profile["Stock"]
        self.store_profile["Coverage"] = self.store_profile["CurrentInventory"]/self.store_profile["AvgMonthlySalesLastQuarter"]
        # Clasificaciones
        self.store_profile["Special"] = False
        self.store_profile.loc[self.store_profile["CodAlmacen"].isin(special_stores), "Special"] = True
        self.store_profile["CoverageClassification"] = \
            np.where(self.store_profile["Coverage"] < self.minimum_acceptable_coverage, "Low coverage",
                     np.where(self.store_profile["Coverage"] <= self.maximum_acceptable_coverage, "OK",
                              "High coverage"))
        # Priorización
        self.store_profile["SortingCoverage"] = self.store_profile["Coverage"].rank(method="dense").astype("int")
        self.store_profile["SortingSales"] = self.store_profile["AnnualSales"].rank(method="dense", ascending=False).astype("int")

    def initial_inventory_level(self, is_special, available, coverage, coverage_class, average_sale, capacity):
        if is_special:
            if available >= 0:
                if coverage != "High coverage":
                    # Hay espacio para poner más ropa... ¡Pongamos más ropa!
                    return min(self.maximum_movement_to_add, available)
                else:
                    # Hay espacio para poner más ropa, pero con lo que tiene aguantará mucho tiempo
                    return 0
            else:
                if coverage_class == "Low coverage":
                    # Hay mucho inventario, pero no aguantará tanto con lo que tiene
                    movement_to_minumum_coverage = self.add_to_aceptable_coverage(coverage, average_sale)
                    movement_to_maximum_capacity = self.add_to_maximum_capacity(capacity, available)
                    return min(self.maximum_movement_to_add, movement_to_minumum_coverage, movement_to_maximum_capacity)
                else:
                    # Es mucho inventario y la tienda aguantará con esta ropa
                    return 0
        else:
            if coverage_class == "High coverage":
                if available < 0:
                    # Hay mucha ropa y durará mucho tiempo ahí si no se quita
                    return max(available, self.maximum_movement_to_remove)
                else:
                    movement_to_maximum_coverage = self.remove_to_aceptable_coverage(coverage, average_sale)
                    movement_to_minumum_capacity = self.remove_to_minumum_capacity(capacity, available)
                    return max(self.maximum_movement_to_remove, movement_to_maximum_coverage, movement_to_minumum_capacity)
            elif coverage_class == "Low coverage":
                if available < 0:
                    # La ropa durará poco en tienda, pero tampoco hay mucho para agregar
                    movement_to_minumum_coverage = self.add_to_aceptable_coverage(coverage, average_sale)
                    movement_to_maximum_capacity = self.add_to_maximum_capacity(capacity, available)
                    return min(self.maximum_movement_to_add, movement_to_minumum_coverage, movement_to_maximum_capacity)
                else:
                    # Hay que agregar ropa y sí hay espacio para agregar
                    return min(available, self.maximum_movement_to_add)
        return 0

    def add_to_aceptable_coverage(self, covarage, average_sale):
        return math.floor((self.minimum_acceptable_coverage - covarage)*average_sale)

    def add_to_maximum_capacity(self, capacity, available):
        return max(math.floor(capacity*(self.maximum_capacity_percentage - 1) + available), 0)

    def remove_to_aceptable_coverage(self, covarage, average_sale):
        return math.ceil((self.maximum_acceptable_coverage - covarage)*average_sale)

    def remove_to_minumum_capacity(self, capacity, available):
        return min(math.ceil(available - capacity*(1 - self.minimum_capacity_percentage)), 0)

    def feasibility_test(self):
        # El proceso de factibilida fue cuidoso a lo largo del proceso, por lo que no se necesitan más condiciones
        condition1 = self.store_profile["ExpectedLevel"].sum() == 0
        # Hay 2 condiciones que se están obviando. Se cree que no debe de afectar el proceso
        # 1. El total de ropa de temporada no puede superar el 50% de las prendas totales en la tienda.
        # 2. Cuidar de no quitar más prendas a una tienda respecto al total de prendas analizadas en esa tienda
        return condition1

    def adding_level_test(self, level, capacity, available, average_sale, movement=1, is_covered=True):
        # Aquí se revisa si se puede agregar más prendas sin pasarse de los límites establecidos
        total_stock = capacity + available
        # ¿Se puede aumentar el nivel sin pasarse del límite de ropa para mover?
        if level >= self.maximum_movement_to_add:
            return False
        # ¿Se puede aumentar el nivel sin sobresaturar la capacidad de la tienda?
        if total_stock + level >= capacity*self.maximum_capacity_percentage:
            return False
        if is_covered:
            # ¿Se puede aumentar el nivel sin sobrepasar la cobertura?
            if (total_stock + level + movement)/average_sale >= self.maximum_acceptable_coverage:
                return False
        return True

    def removing_level_test(self, level, capacity, available, average_sale, fashion_stock, movement=1, is_covered=True):
        # NOTA: no se están considerando tiendas especiales
        total_stock = capacity + available
        # ¿Se puede disminuir el nivel sin pasarse del límite de ropa para mover?
        if level <= self.maximum_movement_to_remove:
            return False
        # ¿Se puede disminuir el nivel sin dejar a la tienda vacía?
        if total_stock + level <= capacity*self.minimum_capacity_percentage:
            return False
        if is_covered:
            # ¿Se puede disminuir el nivel manteniendo una buena cobertura?
            if (total_stock + level + movement)/average_sale <= self.minimum_acceptable_coverage:
                return False
        # ¿La tienda tiene suficiente ropa de las prendas elegidas para poder quitar?
        if level + movement <= fashion_stock:
            return False
        return True
