from views.get_modify_solution_window import GetModifySolutionWindow
import pandas as pd


class GetModifySolutionController:
    def __init__(self, navigation_controller, settings, solution):
        self.navigation_controller = navigation_controller
        self.settings = settings
        self.solution = solution

        print("Esperando modificaciones")
        self.flag_load = False

        self.view = GetModifySolutionWindow()
        self.selected_directory = self.view.path_display.text()
        self.setup_connections()
        self.show()

    def setup_connections(self):
        self.view.button_select_path.clicked.connect(self.select_load_location)
        self.view.button_box.accepted.connect(self.load_solution)
        self.view.button_box.rejected.connect(self.close)

    def select_load_location(self):
        # Abrir cuadro de diálogo para seleccionar un directorio
        new_selected_directory =\
            self.view.selected_directory.getExistingDirectory(self.view, "Seleccione la ubicación del archivo")
        if new_selected_directory:
            # Actualizar la etiqueta de la ruta seleccionada
            self.selected_directory = new_selected_directory.replace("/", "\\") + "\\inventario_final_modificado.csv"
            self.view.path_display.setText(self.selected_directory)

    def load_solution(self):
        storages = self.solution.level_pivot.columns.difference(["index", "Agrupador", "SKU"]).tolist()
        level = self.solution.level_pivot
        df_modified = level

        try:
            df_from_csv = pd.read_csv(self.selected_directory, usecols=["SKU"]+storages)
            df_modified = level[level.columns.difference(storages)].merge(df_from_csv, on=["SKU"])
        except Exception as e:
            print(f"ERROR. {type(e)}: {e}. ¿Seguro que se encuentra el CSV en la ubicación dada?")

        for index in range(len(level)):
            if level[storages].iloc[index].sum() != df_modified[storages].iloc[index].sum():
                print(f"Error. Difiere el inventario en el producto {level['SKU'].iloc[index]}. Difiere en")
                print(f"{int(level[storages].iloc[index].sum() - df_modified[storages].iloc[index].sum())} piezas.")
                break
            for storage in storages:
                if level.iloc[index, level.columns.get_loc(storage)] != \
                        df_modified.iloc[index, df_modified.columns.get_loc(storage)]:
                    self.flag_load = True
                    self.solution.level_pivot = df_modified.copy()
                    break
            if self.flag_load:
                break

        self.close()

    def show(self):
        self.view.show()

    def continue_to_next_window(self):
        if self.flag_load:
            print("Modificación realizada en los niveles finales")
        else:
            print("Se continúa sin modificación en los niveles finales")
        self.navigation_controller.phase_3(self.solution)

    def close(self):
        self.continue_to_next_window()
        self.view.close()
