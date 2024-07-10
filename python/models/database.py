from .connection_manager import ConnectionManager


# Integración de las clases referente a la obtención de datos de la base de datos
# para proporcionar una interfaz centralizada.
class Database:
    def __init__(self, host, database, user, password, port, driver) -> None:
        self.connection_manager = ConnectionManager(host, database, user, password, port, driver)
        self.connection = None
    
    def connect(self):
        if self.connection_manager.connect():
            self.connection = self.connection_manager.get_connection()
            return True
        return False

    def close(self):
        self.connection_manager.close()
