import os
from views.modify_solution_window import ModifySolutionWindow
from models.phase_2 import Phase2
import pandas as pd


class ModifySolutionController:
    def __init__(self, navigation_controller, settings, app_state, levels, file="Nivelacion_modificable.xlsx"):
        self.navigation_controller = navigation_controller
        self.settings = settings
        self.app_state = app_state
        self.levels = levels
        self.file_name = file

        # Campos que se usarán de los productos
        self.product_fields = ["Coleccion", "Modelo", "Color", "SKU"]
        # Bandera de finalización
        self.flag_save = False

        print("Fase 2: Redistribución de productos")
        self.solution = Phase2(self.app_state.df_facts, self.app_state.product_dimensions, self.levels.store_profile)
        self.solution.clean()
        print("Solución calculada")
        self.view = ModifySolutionWindow(self.file_name)
        self.setup_connections()
        self.show()

    def setup_connections(self):
        self.view.button_select_path.clicked.connect(self.select_save_location)
        self.view.button_box.accepted.connect(self.save_solution)
        self.view.button_box.rejected.connect(self.continue_to_next_window)

    def select_save_location(self):
        # Abrir cuadro de diálogo para seleccionar un directorio
        new_selected_directory =\
            self.view.selected_directory.getExistingDirectory(self.view, "Seleccione la ubicación de guardado")
        if new_selected_directory:
            if not self.view.flag_folder_found:
                self.view.flag_folder_found = True
                self.view.path_label.show()
                self.view.path_display.show()
                self.view.button_box.show()
            # Actualizar la etiqueta de la ruta seleccionada
            self.view.selected_file = os.path.join(new_selected_directory, self.file_name)
            self.view.path_display.setText(self.view.selected_file)

    def save_solution(self):
        # Obtener los DataFrames de donde saldrán los datos
        initial_pivot = self.solution.initial_pivot
        level_pivot = self.solution.level_pivot
        sales_pivot = self.solution.sales_pivot
        products = self.solution.product_dimensions
        stores = self.solution.store_profile["CodAlmacen"].tolist()
        wholesales = initial_pivot.columns.difference(["index", "Agrupador", "SKU"] + stores).tolist()

        # Crear las tablas que se van a guardar
        initial = products[self.product_fields].merge(initial_pivot[["SKU"] + stores + wholesales], on=["SKU"])
        level = products[self.product_fields].merge(level_pivot[["SKU"] + stores + wholesales], on=["SKU"])
        sales = products[self.product_fields].merge(sales_pivot[["SKU"] + stores], on=["SKU"])

        # Ordenar por SKU
        initial = initial.sort_values(by=["SKU"])
        level = level.sort_values(by=["SKU"])
        sales = sales.sort_values(by=["SKU"])

        # Crear un writer para poder escribir un archivo con diferentes hojas
        writer = pd.ExcelWriter(self.view.selected_file, engine='xlsxwriter')

        # Guardar los archivos
        initial.to_excel(writer, sheet_name='Inicial', index=False)
        level.to_excel(writer, sheet_name='Nivelado', index=False)
        sales.to_excel(writer, sheet_name='Ventas', index=False)

        # Terminar
        writer.close()
        self.flag_save = True
        self.continue_to_next_window()

    def continue_to_next_window(self):
        if self.flag_save:
            self.close()
            self.navigation_controller.update_solution(self.solution)
        else:
            self.close()
            self.navigation_controller.phase_3(self.solution)

    def show(self):
        self.view.show()

    def close(self):
        self.view.close()
