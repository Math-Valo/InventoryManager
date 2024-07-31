import re

class QueryManager:
    def __init__(self) -> None:
        self.args = {
            "date": "",
            "stores": [],
            "products": []
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
            "sales_pieces": "PiezasVendidas",

            "store_code": "CodAlmacen",
            "store_channel": "Canal",
            "store_brand": "Marca",

            "product_code": "SKU",
            "product_brand": "Marca",
            "product_group": "Grupo",
            "product_code_without_size": "Agrupador"
        }

    def set_default_queries(self) -> None:
        self.set_date_query()
        self.set_store_query()
        self.set_product_query()
        self.set_inventory_and_sales_query()

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
        query = \
        f"""
            SELECT
                *
            FROM
                {self.tables["store"]}
            WHERE
                {self.columns["store_channel"]} = '{condition_store_channel}'
                AND
                {self.columns["store_brand"]} = '{condition_store_brand}'
            ORDER BY
                {self.columns["store_code"]}
        """
        if self.args["date"] != "":
            cut = re.search(r"\n(?=(\s+|\t+)ORDER BY)", query).start()
            additional_condition = \
            f"""
                AND
                {self.columns["store_code"]} IN
                (
                    SELECT
                        {self.columns["inventories_store"]}
                    FROM
                        {self.tables["inventories"]}
                    WHERE
                        {self.columns["inventories_date"]} = '{self.args["date"]}'
                )"""
            query = query[:cut] + additional_condition + query[cut:]
        self.queries["stores_in_inventory"] = query

    def set_product_query(self):
        condition_product_brand = "ABITO"
        condition_product_group = "ROPA"
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
            ORDER BY
                {self.columns["product_code"]}
        """
        if self.args["date"] != "" or len(self.args["stores"]) > 0:
            cut = re.search(r"\n(?=(\s+|\t+)ORDER BY)", query).start()
            condition_date = f"{self.columns['inventories_date']} = '{self.args['date']}'"
            condition_store = f"{self.columns['inventories_store']} IN {self.args['stores'].__str__()}"
            condition_store = condition_store.replace("[","(").replace("]",")")
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
        if self.args["date"] == "":
            return None
        if  len(self.args["stores"]) == 0 and len(self.args["products"]) == 0:
            total_inventories_pieces = "TotalPieces"
            total_sales_pieces = "TotalPieces"
            str_stores = self.args['stores'].__str__().replace("[","(").replace("]",")")
            str_products = self.args['products'].__str__().replace("[","(").replace("]",")")
            query = \
            f"""
                SELECT
                    c.{self.columns["store_code"]},
                    c.{self.columns["product_code"]},
                    COALESCE(i.{total_inventories_pieces}, 0) AS TotalInventories,
                    COALESCE(v.{total_sales_pieces}, 0) AS TotalSales
                    FROM
                    (
                    SELECT
                        s.{self.columns["store_code"]}
                        p.{self.columns["product_code"]}
                    FROM
                        {self.tables["store"]} s
                    CROSS JOIN
                        {self.tables["product"]} P
                    WHERE
                        s.{self.columns["store_code"]} IN {str_stores}
                        AND
                        p.{self.columns["product_code_without_size"]}
                        IN
                        (
                        SELECT
                            {self.columns["product_code_without_size"]}
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
                        {self.tables["product"]}
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
                        {self.columns["inventories_product"]},
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
                    c.{self.columns["store_code"]} = i.{self.columns["sales_store"]}
                    AND
                    c.{self.columns["product_code"]} = i.{self.columns["sales_product"]}
                ORDER BY
                    {self.columns["store_code"]},
                    {self.columns["product_code"]}
            """
            self.queries["inventories_and_sales"] = query

    def get_query(self, query: str) -> str:
        return self.queries.get(query)

if __name__ == "__main__":
    queries = QueryManager()
    queries.set_date("2024-07-12")
    queries.set_stores(["007", "008"])
    queries.set_products(["P1", "P2", "P3"])
    queries.set_default_queries()
    print(queries.get_query("inventories_and_sales"))