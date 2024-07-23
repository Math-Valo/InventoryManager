import json
import os


class ConfigManager():
    def __init__(self, config_file="config/config.json"):
        self.config_file = config_file
        self.settings = dict()
        self.credentials = None
        self.load_config()

    def set_settings(self, key, value):
        self.settings[key] = value
        self.save_config()

    def get_settings(self, key):
        return self.settings.get(key)

    def load_config(self):
        # if os.path.exists(self.config_file):  # No es suficiente que exista, hay que asegurar que no está vacío
        try:
            with open(self.config_file, 'r') as file:
                self.settings = json.load(file)
                self.credentials = self.settings.get('credentials', None)
        except Exception as e:
            print(f"No se pudo leer el JSON: {e}")

    def save_config(self):
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as file:
            json.dump(self.settings, file, indent=1)

if __name__ == "__main__":
    configurar = ConfigManager()
