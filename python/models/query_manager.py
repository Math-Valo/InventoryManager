import re

class QueryManager:
    def __init__(self) -> None:
        self.args = {
            "date": "",
            "stores": [],
            "products": [],
            "store_product": []
        }
        self.tables = dict()
        self.columns = dict()
        self.queries = dict()
        self.default_names()

    def set_date(self, date: str) -> None:
        self.args["date"] = date

    def set_stores(self, store_codes: list) -> None:
        self.args["stores"] = store_codes
    
    def set_products(self, product_codes: list) -> None:
        self.args["products"] = product_codes

    def set_store_product(self, store_product_codes: list) -> None:
        self.args["store_product"] = store_product_codes

    def default_names(self) -> None:
        self.tables = {
            "inventories": "Inventarios",
            "sales": "Ventas",
            "store": "Tiendas",
            "product": "Catalogo"
        }

        self.columns = {
            "inventories_date": "Fecha",
            "inventories_store": "CodAlmacen",
            "inventories_product": "SKU",
            "inventories_pieces": "Unidades",

            "sales_date": "Fecha",
            "sales_store": "CodAlmacen",
            "sales_product": "SKU",
            "sales_pieces": "Piezas",

            "store_code": "CodAlmacen",
            "store_name": "NombreAlmacen",
            "store_channel": "Canal",
            "store_brand": "Marca",

            "product_code": "SKU",
            "product_brand": "Marca",
            "product_group": "Grupo",
            "product_code_without_size": "Agrupador",
            "product_family": "Familia"
        }

    def set_default_queries(self) -> None:
        self.set_date_query()
        self.set_store_query()
        self.set_product_query()
        self.set_inventory_and_sales_query()
        self.set_kpis_query()

    def set_date_query(self):
        query = \
        f"""
            SELECT
                MAX({self.columns["inventories_date"]}) AS UltimaFecha
            FROM
                {self.tables["inventories"]}
        """
        self.queries["last_date_in_inventory"] = query

    def set_store_query(self):
        condition_store_channel = "TIENDAS PROPIAS"
        condition_store_brand = "ABITO"
        condition_store_substring_name_1 = "%OUTLET%"
        condition_store_substring_name_2 = "%PRODUCTO TERMINADO%"
        query = \
        f"""
            SELECT
                s.*
            FROM
                {self.tables["store"]} s
            WHERE
                s.{self.columns["store_brand"]} = '{condition_store_brand}'
                AND
                s.{self.columns["store_name"]} NOT LIKE '{condition_store_substring_name_1}'
                AND
                (
                    s.{self.columns["store_channel"]} = '{condition_store_channel}'
                    OR
                    s.{self.columns["store_name"]} LIKE '{condition_store_substring_name_2}'
                )
            ORDER BY
                s.{self.columns["store_code"]}
        """
        if self.args["date"] != "":
            cut = re.search(r"\n(?=(\s+|\t+)ORDER BY)", query).start()
            additional_condition = \
            f"""
                AND
                s.{self.columns["store_code"]} IN
                (
                    SELECT
                        {self.columns["inventories_store"]}
                    FROM
                        {self.tables["inventories"]}
                    WHERE
                        {self.columns["inventories_date"]} = '{self.args["date"]}'
                )"""
            query = query[:cut] + additional_condition + query[cut:]

            cut = re.search(r"\n(?=(\s+|\t+)FROM)", query).start()
            new_name_for_stock = "Stock"
            additional_condition = \
            f"""
                , COALESCE(i.TotalInventories, 0) AS {new_name_for_stock}"""
            query = query[:cut] + additional_condition + query[cut:]

            cut = re.search(r"\n(?=(\s+|\t+)WHERE)", query).start()
            condition_product_brand = "ABITO"
            condition_product_group = "ROPA"
            condition_product_family_1 = "ZAPATO"
            condition_product_family_2 = "ZAPATOS"
            additional_condition = \
            f"""
            LEFT JOIN
                (
                SELECT
                    i.{self.columns["inventories_store"]},
                    SUM(i.{self.columns["inventories_pieces"]}) AS TotalInventories
                FROM
                    {self.tables["inventories"]} i
                LEFT JOIN
                    {self.tables["product"]} p
                ON
                    i.{self.columns["inventories_product"]} = p.{self.columns["product_code"]}
                WHERE
                    i.{self.columns["inventories_date"]} = '{self.args["date"]}'
                    AND
                    p.{self.columns["product_brand"]} = '{condition_product_brand}'
                    AND
                    p.{self.columns["product_group"]} = '{condition_product_group}'
                    AND
                    p.{self.columns["product_family"]} <> '{condition_product_family_1}'
                    AND
                    p.{self.columns["product_family"]} <> '{condition_product_family_2}'
                GROUP BY
                    i.{self.columns["inventories_store"]}
                ) i
            ON
                s.{self.columns["store_code"]} = i.{self.columns["inventories_store"]}"""
            query = query[:cut] + additional_condition + query[cut:]
        self.queries["stores_in_inventory"] = query

    def set_product_query(self):
        condition_product_brand = "ABITO"
        condition_product_group = "ROPA"
        condition_product_family_1 = "ZAPATO"
        condition_product_family_2 = "ZAPATOS"
        query = \
        f"""
            SELECT
                *
            FROM
                {self.tables["product"]}
            WHERE
                {self.columns["product_brand"]} = '{condition_product_brand}'
                AND
                {self.columns["product_group"]} = '{condition_product_group}'
                AND
                {self.columns["product_family"]} <> '{condition_product_family_1}'
                AND
                {self.columns["product_family"]} <> '{condition_product_family_2}'
            ORDER BY
                {self.columns["product_code"]}
        """
        if self.args["date"] != "" or len(self.args["stores"]) > 0:
            cut = re.search(r"\n(?=(\s+|\t+)ORDER BY)", query).start()
            str_stores = self.args['stores'].__str__().replace("[","(").replace("]",")")
            condition_date = f"{self.columns['inventories_date']} = '{self.args['date']}'"
            condition_store = f"{self.columns['inventories_store']} IN {str_stores}"
            if self.args["date"] == "":
                condition_inventories = f"""
                        {condition_store}"""
            elif len(self.args["stores"]) == 0:
                condition_inventories = f"""
                        {condition_date}"""
            else:
                condition_inventories = \
                f"""
                        {condition_date}
                        AND
                        {condition_store}"""
            additional_condition = \
            f"""
                AND
                {self.columns["product_code"]} IN
                (
                    SELECT
                        {self.columns["inventories_product"]}
                    FROM
                        {self.tables["inventories"]}
                    WHERE {condition_inventories}
                )"""
            query = query[:cut] + additional_condition + query[cut:]
        self.queries["products_in_inventory"] = query

    def set_inventory_and_sales_query(self):
        if self.args["date"] == "" or len(self.args["stores"]) == 0 or len(self.args["products"]) == 0:
            return None
        total_inventories_pieces = "TotalPieces"
        total_sales_pieces = "TotalPieces"
        str_stores = self.args['stores'].__str__().replace("[","(").replace("]",")")
        str_products = self.args['products'].__str__().replace("[","(").replace("]",")")
        query = \
        f"""
            SELECT
                c.{self.columns["store_code"]},
                c.{self.columns["product_code"]},
                COALESCE(i.{total_inventories_pieces}, 0) AS CurrentInventory,
                COALESCE(v.{total_sales_pieces}, 0) AS AnnualSales
            FROM
                (
                SELECT
                    s.{self.columns["store_code"]},
                    p.{self.columns["product_code"]}
                FROM
                    {self.tables["store"]} s
                CROSS JOIN
                    {self.tables["product"]} p
                WHERE
                    s.{self.columns["store_code"]} IN {str_stores}
                    AND
                    p.{self.columns["product_code_without_size"]}
                    IN
                    (
                    SELECT
                        DISTINCT {self.columns["product_code_without_size"]}
                    FROM
                        {self.tables["product"]}
                    WHERE
                        {self.columns["product_code"]} IN {str_products}
                    )
                ) c
            LEFT JOIN
                (
                SELECT
                    {self.columns["inventories_store"]},
                    {self.columns["inventories_product"]},
                    SUM({self.columns["inventories_pieces"]}) AS {total_inventories_pieces}
                FROM
                    {self.tables["inventories"]}
                WHERE
                    {self.columns["inventories_date"]} = '{self.args["date"]}'
                    AND
                    {self.columns["inventories_pieces"]} > 0
                GROUP BY
                    {self.columns["inventories_store"]},
                    {self.columns["inventories_product"]}
                ) i
            ON
                c.{self.columns["store_code"]} = i.{self.columns["inventories_store"]}
                AND
                c.{self.columns["product_code"]} = i.{self.columns["inventories_product"]}
            LEFT JOIN
                (
                SELECT
                    {self.columns["sales_store"]},
                    {self.columns["sales_product"]},
                    SUM({self.columns["sales_pieces"]}) AS {total_sales_pieces}
                FROM
                    {self.tables["sales"]}
                WHERE
                    {self.columns["sales_date"]}
                    BETWEEN
                    DATE_SUB('{self.args["date"]}', INTERVAL 1 YEAR)
                    AND 
                    '{self.args["date"]}'
                GROUP BY
                    {self.columns["sales_store"]},
                    {self.columns["sales_product"]}
                ) v
            ON
                c.{self.columns["store_code"]} = v.{self.columns["sales_store"]}
                AND
                c.{self.columns["product_code"]} = v.{self.columns["sales_product"]}
            ORDER BY
                c.{self.columns["store_code"]},
                c.{self.columns["product_code"]}
        """
        self.queries["inventories_and_sales"] = query

    def set_kpis_query(self):
        if self.args["date"] == "" or len(self.args["store_product"]) == 0:
            return None
        # 0. Definición de variables que serán útiles
        store_product_str = self.args["store_product"].__str__().replace("[", "(").replace("]", ")")
        # 1. Ventas del último trimestre
        total_sales_pieces = "TotalPieces"
        query = \
        f"""
            SELECT
                {self.columns["sales_store"]},
                {self.columns["sales_product"]},
                COALESCE(SUM({self.columns["sales_pieces"]}), 0) AS QuarterlyPieceSales
            FROM
                {self.tables["sales"]}
            WHERE
                {self.columns["sales_date"]}
                BETWEEN
                DATE_SUB('{self.args["date"]}', INTERVAL 3 MONTH)
                AND
                '{self.args["date"]}'
                AND
                ({self.columns["sales_store"]}, {self.columns["sales_product"]}) IN {store_product_str}
            GROUP BY
                {self.columns["sales_store"]},
                {self.columns["sales_product"]}
        """
        self.queries["quarter_sales"] = query

    def get_query(self, query: str) -> str:
        return self.queries.get(query)

if __name__ == "__main__":
    queries = QueryManager()
    queries.set_date("2024-07-12")
    queries.set_stores(["007", "008"])
    queries.set_products(["P1", "P2", "P3"])
    queries.set_default_queries()
    print(queries.get_query("inventories_and_sales"))