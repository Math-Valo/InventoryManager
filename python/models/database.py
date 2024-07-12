from .connection_manager import ConnectionManager


# Integración de las clases referente a la obtención de datos de la base de datos
# para proporcionar una interfaz centralizada.
class Database:
    def __init__(self) -> None:
        self.connection_manager = ConnectionManager()
        self.connection = None

    def set_credentials(self, host, database, user, password, port, driver) -> None:
        self.connection_manager.set_credentials(host, database, user, password, port, driver)
    
    def connect(self):
        if self.connection_manager.connect():
            self.connection = self.connection_manager.get_connection()
            return True
        return False

    # def close(self):
    #     self.connection_manager.close()
