import sqlalchemy as sa


class ConnectionManager:
    def __init__(self, host="", database="", user="", password="", port=0, driver="") -> None:
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.driver = driver
        self.engine = None
        self.connection = None

    def set_credentials(self, host, database, user, password, port, driver) -> None:
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.driver = driver

    def connect(self):
        try:
            connection_url = sa.engine.URL.create(
                drivername="mysql+pyodbc",  # Requiere tener instalado el módulo pyodbc
                host=self.host,
                database=self.database,
                username=self.user,
                password=self.password,
                port=self.port,
                query=dict(
                    driver=self.driver,
                    MULTI_HOST="1"  # Evita errores generados por incluir el puerto
                )
            )
            self.engine = sa.create_engine(connection_url)
            self.connection = self.engine.connect()
            self.connection.close()
            return True
        except Exception as e:
            print(f"Error al conectar la base de datos: {e}")
            return False
        
    def close(self):
        self.engine.dispose()

    def get_engine(self):
        return self.engine
