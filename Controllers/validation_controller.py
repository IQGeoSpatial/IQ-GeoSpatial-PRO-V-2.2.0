from Services.validation_service import ValidationService

class ValidationController:
    def __init__(self, view):
        self.view = view
        self.service = ValidationService()

    def start_validation(self, root_path, selected_optionals):
        """ Inicia la validación y muestra los resultados en la vista. """
        try:
            report = self.service.validate_expediente(root_path, selected_optionals)
            self.view.show_results(report)
        except Exception as e:
            self.view.show_message("Error", f"Ocurrió un error inesperado durante la validación:\n{e}", "error")

    def save_report(self, file_path, content):
        """ Guarda el contenido del reporte en un archivo de texto. """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.view.show_message("Éxito", f"Reporte guardado exitosamente en:\n{file_path}")
        except Exception as e:
            self.view.show_message("Error al Guardar", f"No se pudo guardar el archivo:\n{e}", "error")
