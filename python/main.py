from models.config_manager import ConfigManager
from controllers.navigation_controller import NavigationController


def main():
    settings = ConfigManager()
    navigation_controller = NavigationController(settings)
    navigation_controller.run()

if __name__ == "__main__":
    main()
