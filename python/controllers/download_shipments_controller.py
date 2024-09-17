import os
from views.download_shipments_window import DownloadShipmentsWindow
from models.phase_3 import Phase3
import pandas as pd


class DownloadShipmentsController:
    def __init__(self, navigation_controller, settings, app_state, solution, file="Nivelacion_envios.xlsx"):
        self.navigation_controller = navigation_controller
        self.settings = settings
        self.app_state = app_state
        self.solution = solution
        self.file_name = file

        # Bandera de finalización
        self.flag_save = False

        print("Fase 3: Determinación de los envíos")
        self.shipments = Phase3(self.solution.initial_pivot, self.solution.level_pivot, self.solution.store_profile,
                                self.app_state.get_store_dimensions())
        print("Envíos determinados")
        print("El proceso de nivelación ha finalizado.")
        self.view = DownloadShipmentsWindow(self.file_name)
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
        # Obtener el DataFrames de donde saldrán los datos
        shipments = self.shipments.shipments.copy()
        product_dimension = self.app_state.get_product_dimensions()
        store_dimension = self.app_state.get_store_dimensions()

        # Agregar detalles al DataFrame de envíos
        shipments = shipments.merge(product_dimension[["SKU", "Descripcion"]], left_on=["sku"], right_on=["SKU"])
        shipments = shipments.merge(store_dimension[["CodAlmacen", "NombreAlmacen"]], left_on=["receiving"],
                                    right_on=["CodAlmacen"])

        # Crear un writer para poder escribir un archivo con diferentes hojas
        writer = pd.ExcelWriter(self.view.selected_file, engine='xlsxwriter')

        # Crear y guardar las tablas para cada tienda que envía productos
        try:
            for shipping_store in shipments["sending"].unique().tolist():
                sheet_name = store_dimension.loc[store_dimension["CodAlmacen"] == shipping_store,
                                                 "NombreAlmacen"].iloc[0]
                df = shipments[shipments["sending"] == shipping_store
                               ][["NombreAlmacen", "sku", "Descripcion", "shipping"]].reset_index(drop=True)
                df.rename(columns={"NombreAlmacen": "Tienda", "sku": "Producto", "Descripcion": "Descripción",
                                   "shipping": "Envíos"})
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            writer.close()
            self.flag_save = True
        except Exception as e:
            print(f"Error al guardar el archivo. {type(e)}: {e}.\nNo se guardó el archivo.")
            writer.close()

        self.continue_to_next_window()

    def continue_to_next_window(self):
        if self.flag_save:
            print("Archivo de envios guardado correctamente")
        else:
            print("No se guardaron los envios")
        self.close()
        self.navigation_controller.exit_application()

    def show(self):
        self.view.show()

    def close(self):
        self.view.close()
