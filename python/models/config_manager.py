import json
import os


class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.find_config_folder()

        self.settings = dict()
        self.credentials = None
        self.load_config()

    def find_config_folder(self, config_folder="config"):
        current_path = os.path.dirname(__file__)
        while not os.path.exists(os.path.join(current_path, config_folder)):
            parent_path = os.path.dirname(current_path)
            if current_path == parent_path:
                raise FileNotFoundError(f"No se pudo encontrar {config_folder}")
            current_path = parent_path
        self.config_file = os.path.join(current_path, config_folder, self.config_file)

    def set_settings(self, key, value):
        self.settings[key] = value
        self.save_config()

    def get_settings(self, key, default=None):
        return self.settings.get(key, default)

    def load_config(self):
        try:
            with open(self.config_file, 'r') as file:
                self.settings = json.load(file)
                self.credentials = self.settings.get('credentials', None)
        except Exception as e:
            print(f"No se pudo leer el JSON: {e}")
            self.settings = {}

    def save_config(self):
        settings = self.settings
        if "database_connection" in settings.keys():
            del settings["database_connection"]
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as file:
            json.dump(settings, file, indent=1)


if __name__ == "__main__":
    configurar = ConfigManager()
