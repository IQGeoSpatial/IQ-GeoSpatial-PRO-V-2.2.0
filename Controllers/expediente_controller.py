
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QApplication
from utils.folder_structure import ExpedienteBuilder
from Services.word_service import WordGenerator


class ExpedienteController:
    def __init__(self, model, view, db):
        self.model = model
        self.view = view
        self.db = db

    def generar_codigos(self):
        try:
            cod_base_str = self.view.cod_base.currentText()
            num_codigos_str = self.view.num_codigos.currentText()
            incremento_str = self.view.incremento.currentText()

            if not all([cod_base_str, num_codigos_str, incremento_str]):
                self.view.lbl_codigos.setText("Por favor, complete todos los campos.")
                self.view.lbl_codigos.setObjectName("Error")
                return

            cod_base = int(cod_base_str)
            num_codigos = int(num_codigos_str)
            incremento = int(incremento_str)

            self.db.limpiar_codigos() # Limpia códigos anteriores antes de generar nuevos
            
            for i in range(num_codigos):
                codigo_actual = str(cod_base + (i * incremento))
                self.db.agregar_codigo(codigo_actual)

            self.view.lbl_codigos.setText(f"Se generaron {num_codigos} códigos.")
            self.view.lbl_codigos.setObjectName("Success")
            self.view.btn_ver_codigos.show()

        except ValueError:
            self.view.lbl_codigos.setText("Error: Ingrese solo números válidos.")
            self.view.lbl_codigos.setObjectName("Error")
        except Exception as e:
            self.view.lbl_codigos.setText(f"Error inesperado: {e}")
            self.view.lbl_codigos.setObjectName("Error")

    def eliminar_codigo_dialog(self, codigo, dialog):
        reply = QMessageBox.question(self.view, 'Confirmar Eliminación',
            f"¿Está seguro de que desea eliminar el código '{codigo}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.eliminar_codigo(codigo)
            self.view.actualizar_lista_codigos(dialog)

    def editar_codigo_dialog(self, codigo_antiguo, dialog):
        nuevo_codigo, ok = QInputDialog.getText(self.view, 'Editar Código', 'Ingrese el nuevo código:', text=codigo_antiguo)
        if ok and nuevo_codigo:
            self.db.editar_codigo(codigo_antiguo, nuevo_codigo.strip())
            self.view.actualizar_lista_codigos(dialog)

    def agregar_fecha_lectura(self, fecha):
        if not hasattr(self.view, 'fechas_lectura'):
            self.view.fechas_lectura = []
        
        if any(f[0] == fecha for f in self.view.fechas_lectura):
            return

        self.view.fechas_lectura.append((fecha, None))

    def _rellenar_docx(self, doc, contexto):
        """
        Busca y reemplaza placeholders en párrafos y tablas de un documento .docx.
        Los placeholders deben tener el formato {{NOMBRE_COLUMNA}}.
        """
        # Reemplazar en párrafos
        for p in doc.paragraphs:
            # Es necesario un bucle while para reemplazar múltiples placeholders en el mismo párrafo
            for key, value in contexto.items():
                if key in p.text:
                    # Reemplazar en cada 'run' para mantener el formato
                    for run in p.runs:
                        if key in run.text:
                            run.text = run.text.replace(key, str(value))

        # Reemplazar en tablas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        for key, value in contexto.items():
                            if key in p.text:
                                for run in p.runs:
                                    if key in run.text:
                                        run.text = run.text.replace(key, str(value))
        return doc

    def generar_formularios_word(self, excel_path, output_dir, seleccionados, image_paths_dict=None, zona=None, orden=None):
        try:
            generator = WordGenerator(excel_path, output_dir, seleccionados)
            # Pasar zona y orden al generador de formularios
            if image_paths_dict is not None:
                zip_path = generator.generar_formularios(
                    image_paths_dict=image_paths_dict,
                    zona=zona,
                    orden=orden
                )
            else:
                zip_path = generator.generar_formularios(
                    zona=zona,
                    orden=orden
                )
            return True, zip_path
        except Exception as e:
            return False, str(e)

    def crear_expediente_estructura(self, expediente, puntos, agregar_video, agregar_verif, carpeta_base, fechas_pg):
        """
        Orquesta la creación de la estructura de carpetas del expediente
        usando la clase ExpedienteBuilder.
        """
        try:
            builder = ExpedienteBuilder(
                expediente=expediente,
                puntos=puntos,
                agregar_video=agregar_video,
                agregar_verif=agregar_verif,
                carpeta_base=carpeta_base,
                fechas_pg=fechas_pg
            )
            builder.build()
            return True, f"¡Carpetas del expediente '{expediente}' creadas con éxito!"
        except Exception as e:
            return False, f"Error al crear la estructura: {str(e)}"