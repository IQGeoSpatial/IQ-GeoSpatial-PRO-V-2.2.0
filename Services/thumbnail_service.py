import os
import comtypes.client
import tempfile
import fitz  # PyMuPDF
from PyQt5.QtCore import QObject, pyqtSignal

class ThumbnailWorker(QObject):
    """
    Worker to generate thumbnails from .docx files in a background thread.
    It converts docx to a temporary PDF, then extracts page images from the PDF.
    """
    thumbnail_generated = pyqtSignal(str, str, int) # doc_name, thumb_path, page_num
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, doc_paths, single_file_mode=False):
        super().__init__()
        self.doc_paths = doc_paths
        self.single_file_mode = single_file_mode
        self.is_running = True
        self.temp_dir = tempfile.mkdtemp(prefix="iq_thumb_")

    def stop(self):
        self.is_running = False

    def run(self):
        word_app = None
        try:
            comtypes.CoInitialize()
            word_app = comtypes.client.CreateObject('Word.Application')
            word_app.Visible = False

            for doc_path in self.doc_paths:
                if not self.is_running:
                    break
                
                temp_pdf_path = os.path.join(self.temp_dir, os.path.basename(doc_path) + ".pdf")
                
                try:
                    doc = word_app.Documents.Open(os.path.abspath(doc_path))
                    doc.SaveAs(os.path.abspath(temp_pdf_path), FileFormat=17)
                    doc.Close(SaveChanges=0)

                    pdf_doc = fitz.open(temp_pdf_path)
                    pages_to_render = range(len(pdf_doc)) if self.single_file_mode else [0]

                    for page_num in pages_to_render:
                        if not self.is_running: break
                        page = pdf_doc.load_page(page_num)
                        pix = page.get_pixmap(dpi=72) # DPI bajo para miniaturas rápidas
                        temp_img_path = os.path.join(self.temp_dir, f"{os.path.splitext(os.path.basename(doc_path))[0]}_p{page_num + 1}.png")
                        pix.save(temp_img_path)
                        self.thumbnail_generated.emit(os.path.basename(doc_path), temp_img_path, page_num + 1)
                    pdf_doc.close()
                    os.remove(temp_pdf_path)
                except Exception as e:
                    self.error.emit(f"Error procesando '{os.path.basename(doc_path)}': {e}")
        except Exception as e:
            self.error.emit(f"Error al iniciar Word o procesar archivos: {e}")
        finally:
            if word_app: word_app.Quit()
            comtypes.CoUninitialize()
            self.finished.emit()