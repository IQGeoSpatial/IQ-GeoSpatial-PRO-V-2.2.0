import os
import zipfile
import tempfile
import shutil
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QThread
from Services.pdf_service import PdfConversionWorker
from Services.thumbnail_service import ThumbnailWorker

class PdfConverterController:
    def __init__(self, view):
        self.view = view
        self.source_path = None
        self.output_dir = None
        self.worker_thread = None
        self.worker = None
        self.thumbnail_worker_thread = None
        self.thumbnail_worker = None
        self.docx_files_to_convert = []
        self.temp_zip_dir = None # Para manejar archivos extraídos de un ZIP

    def select_file(self):
        """Selecciona un único archivo .docx."""
        path, _ = QFileDialog.getOpenFileName(self.view, "Seleccionar Archivo Word", "", "Word Files (*.docx)")
        if path:
            self._process_source(path, single_file_mode=True)

    def select_folder(self):
        """Selecciona una carpeta que contiene archivos .docx."""
        path = QFileDialog.getExistingDirectory(self.view, "Seleccionar Carpeta con Archivos Word")
        if path:
            self._process_source(path)

    def select_zip(self):
        """Selecciona un archivo .zip que contiene archivos .docx."""
        path, _ = QFileDialog.getOpenFileName(self.view, "Seleccionar Archivo ZIP", "", "ZIP Files (*.zip)")
        if path:
            self._process_source(path)

    def _process_source(self, path, single_file_mode=False):
        """Centraliza la lógica para procesar la fuente y generar miniaturas."""
        self.source_path = path
        self.view.update_source_label(path)
        self.view.clear_thumbnails()
        self.view.log("Analizando fuente...")

        # Limpiar directorio temporal anterior si existe
        self.cleanup_temp_dir()

        if path.lower().endswith('.docx'):
            self.docx_files_to_convert = [path]
        elif path.lower().endswith('.zip'):
            self.temp_zip_dir = tempfile.mkdtemp(prefix="iq_zip_extract_")
            self.docx_files_to_convert = []
            with zipfile.ZipFile(path, 'r') as zip_ref:
                for member in zip_ref.infolist():
                    if not member.is_dir() and member.filename.lower().endswith('.docx') and not member.filename.startswith('__MACOSX'):
                        extracted_path = zip_ref.extract(member, self.temp_zip_dir)
                        self.docx_files_to_convert.append(extracted_path)
        else: # Es una carpeta
            self.docx_files_to_convert = [
                os.path.join(root, file)
                for root, _, files in os.walk(path)
                for file in files if file.lower().endswith('.docx')
            ]

        if not self.docx_files_to_convert:
            self.view.log("No se encontraron archivos .docx en la fuente seleccionada.")
            return

        self.view.docx_files = self.docx_files_to_convert  # <-- Añade esto aquí

        self._start_thumbnail_generation(self.docx_files_to_convert, single_file_mode)

    def _start_thumbnail_generation(self, doc_paths, single_file_mode):
        """Inicia el worker para generar las miniaturas en segundo plano."""
        self.view.set_controls_enabled(False)
        self.view.log(f"Generando vistas previas para {len(doc_paths)} documento(s)...")

        self.thumbnail_worker_thread = QThread()
        self.thumbnail_worker = ThumbnailWorker(doc_paths, single_file_mode)
        self.thumbnail_worker.moveToThread(self.thumbnail_worker_thread)

        self.thumbnail_worker.thumbnail_generated.connect(self.view.add_thumbnail)
        self.thumbnail_worker.finished.connect(self.on_thumbnails_finished)
        self.thumbnail_worker.error.connect(self.view.log)

        self.thumbnail_worker_thread.started.connect(self.thumbnail_worker.run)
        self.thumbnail_worker_thread.start()

    def start_conversion(self):
        if not self.docx_files_to_convert:
            self.view.log("No hay archivos seleccionados para convertir. Por favor, seleccione una fuente.")
            return

        self.output_dir = QFileDialog.getExistingDirectory(self.view, "Seleccionar Carpeta de Destino para los PDF")
        if not self.output_dir:
            return

        self.view.log("Iniciando conversión...")
        self.view.progress_bar.setValue(0)

        self.worker_thread = QThread()
        # El worker ahora recibirá la lista de archivos directamente
        self.worker = PdfConversionWorker(self.docx_files_to_convert, self.output_dir)
        self.worker.moveToThread(self.worker_thread)

        self.worker.log_message.connect(self.view.log)
        self.worker.progress_update.connect(self.view.progress_bar.setValue)
        self.worker.finished.connect(self.on_conversion_finished)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    def on_thumbnails_finished(self):
        self.view.log("Vistas previas generadas.")
        self.view.set_controls_enabled(True)
        if self.thumbnail_worker_thread:
            self.thumbnail_worker_thread.quit()
            self.thumbnail_worker_thread.wait()
        self.thumbnail_worker_thread = None
        self.thumbnail_worker = None

    def on_conversion_finished(self):
        self.view.log("Proceso de conversión finalizado.")
        self.view.set_controls_enabled(True)
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        self.worker_thread = None
        self.worker = None

    def cancel_conversion(self):
        """Detiene cualquier proceso en segundo plano."""
        if self.worker:
            self.worker.stop()
        if self.thumbnail_worker:
            self.thumbnail_worker.stop()
        self.cleanup_temp_dir()

    def cleanup_temp_dir(self):
        if self.temp_zip_dir and os.path.exists(self.temp_zip_dir):
            shutil.rmtree(self.temp_zip_dir, ignore_errors=True)
            self.temp_zip_dir = None