import os
import comtypes.client
from PyQt5.QtCore import QObject, pyqtSignal

class PdfConversionWorker(QObject):
    """
    Worker que se ejecuta en un hilo separado para convertir archivos .docx a .pdf
    usando la automatización COM de Microsoft Word.
    """
    log_message = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, docx_files, output_dir):
        super().__init__()
        self.docx_files = docx_files
        self.output_dir = output_dir
        self.is_running = True

    def stop(self):
        """Permite detener el proceso de conversión de forma segura."""
        self.is_running = False

    def run(self):
        """Método principal que ejecuta la lógica de conversión."""
        word_app = None
        try:
            word_files = self.docx_files
            if not word_files:
                self.log_message.emit("No se encontraron archivos .docx para convertir.")
                self.finished.emit()
                return

            total_files = len(word_files)
            self.log_message.emit(f"Se encontraron {total_files} archivo(s) .docx para convertir.")
            
            comtypes.CoInitialize()
            word_app = comtypes.client.CreateObject('Word.Application')
            word_app.Visible = False

            for i, file_path in enumerate(word_files):
                if not self.is_running:
                    self.log_message.emit("Conversión cancelada por el usuario.")
                    break
                
                original_name = os.path.basename(file_path)
                self.log_message.emit(f"Convirtiendo: {original_name}...")
                
                try:
                    doc = word_app.Documents.Open(os.path.abspath(file_path))
                    pdf_path = os.path.join(self.output_dir, os.path.splitext(original_name)[0] + '.pdf')
                    doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17) # 17 es el formato para PDF
                    doc.Close(SaveChanges=0)
                    self.log_message.emit(f"Éxito: '{original_name}' -> '{os.path.basename(pdf_path)}'")
                except Exception as e:
                    self.log_message.emit(f"ERROR al convertir '{original_name}': {e}")
                
                progress = int(((i + 1) / total_files) * 100)
                self.progress_update.emit(progress)

        except Exception as e:
            self.log_message.emit(f"ERROR general en el proceso: {e}")
        finally:
            if word_app:
                word_app.Quit()
            comtypes.CoUninitialize()
            self.finished.emit()