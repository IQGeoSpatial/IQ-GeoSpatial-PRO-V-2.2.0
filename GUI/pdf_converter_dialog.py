import os
import tempfile
import shutil
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QProgressBar, QScrollArea, QWidget, QGridLayout,
    QApplication, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from utils.resource_path import resource_path
from Controllers.pdf_converter_controller import PdfConverterController
from PyPDF2 import PdfMerger
import comtypes.client

class PdfConverterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = PdfConverterController(self)
        self.init_ui()
        self.connect_signals()
        self.thumbnail_widgets = []
        self.docx_files = []

    def init_ui(self):
        self.setWindowTitle("Convertidor de Word a PDF")
        self.setObjectName("PdfConverterDialog")
        logo_path = resource_path(os.path.join("Assets", "Image", "convertPDF.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        self.setMinimumSize(970, 900) # Ventana más ancha y alta

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel("Convertir Documentos a PDF")
        title_label.setObjectName("Titulo")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Selection Buttons (replaces GroupBox)
        selection_layout = QHBoxLayout()
        selection_layout.setAlignment(Qt.AlignCenter)
        selection_layout.setSpacing(25)

        # Botón para archivo único
        self.btn_select_file = QPushButton()
        self.btn_select_file.setToolTip("Seleccionar un único archivo Word (.docx)")
        icon_path_word = resource_path(os.path.join("Assets", "Image", "word.png"))
        if os.path.exists(icon_path_word):
            self.btn_select_file.setIcon(QIcon(icon_path_word))
        else:
            self.btn_select_file.setText("W") # Fallback si no hay icono

        # Botón para carpeta
        self.btn_select_folder = QPushButton()
        self.btn_select_folder.setToolTip("Seleccionar una carpeta con archivos Word")
        icon_path_folder = resource_path(os.path.join("Assets", "Image", "FILE.png")) # Reutilizando icono
        if os.path.exists(icon_path_folder):
            self.btn_select_folder.setIcon(QIcon(icon_path_folder))

        # Botón para archivo ZIP
        self.btn_select_zip = QPushButton()
        self.btn_select_zip.setToolTip("Seleccionar un archivo comprimido (.zip)")
        icon_path_zip = resource_path(os.path.join("Assets", "Image", "ZIP.png"))
        if os.path.exists(icon_path_zip):
            self.btn_select_zip.setIcon(QIcon(icon_path_zip))
        else:
            self.btn_select_zip.setText("Z") # Fallback si no hay icono

        # Estilo común para los botones de selección
        for btn in [self.btn_select_file, self.btn_select_folder, self.btn_select_zip]:
            btn.setFixedSize(60, 60)
            btn.setIconSize(QSize(32, 32))
            btn.setObjectName("SelectSourceButton") # Para aplicar estilo desde el tema

        selection_layout.addWidget(self.btn_select_file)
        selection_layout.addWidget(self.btn_select_folder)
        selection_layout.addWidget(self.btn_select_zip)
        main_layout.addLayout(selection_layout)

        main_layout.addSpacing(15) # Espacio adicional

        self.lbl_source = QLabel("Fuente no seleccionada.")
        self.lbl_source.setObjectName("InfoLabel")
        self.lbl_source.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.lbl_source)

        # Thumbnail Area (sin el borde del QGroupBox)
        thumbnail_area_widget = QWidget()
        thumbnail_group_layout = QVBoxLayout(thumbnail_area_widget)
        thumbnail_group_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Quita cualquier borde visible del área de miniaturas
        self.scroll_area.setStyleSheet("QScrollArea, QScrollArea > QWidget, QScrollArea > QFrame, QScrollArea > QAbstractScrollArea { border: none; background: transparent; }")

        self.thumbnail_container = QWidget()
        self.thumbnail_container.setStyleSheet("background: transparent; border: none;")
        self.thumbnail_grid = QGridLayout(self.thumbnail_container)
        self.thumbnail_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.thumbnail_grid.setSpacing(15)

        self.scroll_area.setWidget(self.thumbnail_container)
        thumbnail_group_layout.addWidget(self.scroll_area)
        main_layout.addWidget(thumbnail_area_widget, stretch=1) # Darle más espacio

        # Status Label (replaces log edit)
        self.lbl_status = QLabel("Seleccione una fuente para comenzar.")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setObjectName("StatusLabel")
        main_layout.addWidget(self.lbl_status)

        # Progress and Convert
        bottom_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("ModernProgressBar")
        self.progress_bar.setValue(0)
        bottom_layout.addWidget(self.progress_bar)
        main_layout.addLayout(bottom_layout)

        
        self.btn_convert = QPushButton("CONVERTIR PDF")
        self.btn_convert.setToolTip("Convierte los archivos Word seleccionados a PDF")
        self.btn_convert.setIconSize(QSize(22, 22))
        icon_path_convert = resource_path(os.path.join("Assets", "Image", "convertPDF.png"))
        if os.path.exists(icon_path_convert):
            self.btn_convert.setIcon(QIcon(icon_path_convert))

        self.btn_convertir_unir = QPushButton("CONVERTIR Y UNIR")
        self.btn_convertir_unir.setToolTip("Convierte todos los Word y une los PDFs en uno solo")
        self.btn_convertir_unir.setIconSize(QSize(22, 22))
        icon_path_unir = resource_path(os.path.join("Assets", "Image", "convertPDF.png"))
        if os.path.exists(icon_path_unir):
            self.btn_convertir_unir.setIcon(QIcon(icon_path_unir))

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.btn_convert)
        h_layout.addWidget(self.btn_convertir_unir)
        main_layout.addLayout(h_layout)

        self.btn_convertir_unir.clicked.connect(self.convertir_y_unir_pdf)
        
    
    def convertir_y_unir_pdf(self):
        # 1. Carpeta temporal para PDFs
        temp_pdf_dir = tempfile.mkdtemp(prefix="iq_pdf_unir_")
        pdf_files = []
        errores = []

        # 2. Convertir DOCX a PDF en la carpeta temporal
        for docx_file in self.docx_files:
            try:
                pdf_path = convertir_docx_a_pdf(docx_file, temp_pdf_dir)
                if os.path.exists(pdf_path):
                    pdf_files.append(pdf_path)
                else:
                    errores.append(pdf_path)
            except Exception as e:
                errores.append(str(e))

        if errores:
            QMessageBox.warning(self, "Error de conversión", f"No se pudieron convertir algunos archivos:\n{errores}")

        # 3. Seleccionar carpeta destino para el PDF unido
        output_dir = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Destino para el PDF unido")
        if not output_dir:
            shutil.rmtree(temp_pdf_dir)  # Limpia carpeta temporal
            return

        # 4. Unir los PDFs
        pdf_files = [f for f in pdf_files if os.path.exists(f)]
        if pdf_files:
            merger = PdfMerger()
            for pdf in pdf_files:
                try:
                    merger.append(pdf)
                except Exception as e:
                    QMessageBox.warning(self, "Error al unir", f"No se pudo unir el archivo:\n{pdf}\n{e}")
            output_path = os.path.join(output_dir, "INFORME_GENERAL.pdf")
            merger.write(output_path)
            merger.close()
            QMessageBox.information(self, "PDF unido", f"PDF combinado guardado en:\n{output_path}")
        else:
            QMessageBox.warning(self, "Sin PDFs", "No se generaron archivos PDF para unir.")

        # 5. Eliminar carpeta temporal
        shutil.rmtree(temp_pdf_dir)

    def connect_signals(self):
        self.btn_select_file.clicked.connect(self.controller.select_file)
        self.btn_select_folder.clicked.connect(self.controller.select_folder)
        self.btn_select_zip.clicked.connect(self.controller.select_zip)
        self.btn_convert.clicked.connect(self.start_conversion_with_feedback)

    def start_conversion_with_feedback(self):
        self.log("Convirtiendo documentos... Por favor espere.")
        self.progress_bar.setValue(0)
        self.controller.start_conversion()

    def update_source_label(self, path):
        self.lbl_source.setText(f"<b>{os.path.basename(path)}</b>")

    def log(self, message):
        """Actualiza la etiqueta de estado y la barra de progreso con mensajes del worker."""
        self.lbl_status.setText(message)
        self.progress_bar.setFormat(message)
        self.progress_bar.setTextVisible(True)
        QApplication.processEvents()

    def clear_thumbnails(self):
        """Elimina todas las miniaturas de la cuadrícula."""
        for widget in self.thumbnail_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self.thumbnail_widgets = []

    def add_thumbnail(self, doc_name, thumb_path, page_num):
        """Crea y añade un widget de miniatura a la cuadrícula."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        img_label = QLabel()
        pixmap = QPixmap(thumb_path)
        img_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setFixedSize(120, 120)
        img_label.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; background: white;")

        # Si es un solo archivo, muestra el número de página. Si no, el nombre del archivo.
        if self.controller.source_path.lower().endswith('.docx'):
            label_text = f"Página {page_num}"
        else:
            label_text = doc_name
        
        text_label = QLabel(label_text)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)

        layout.addWidget(img_label)
        layout.addWidget(text_label)
        widget.setFixedSize(140, 160)

        # Añadir a la cuadrícula de 5 columnas
        row = len(self.thumbnail_widgets) // 6
        col = len(self.thumbnail_widgets) % 6
        self.thumbnail_grid.addWidget(widget, row, col)
        self.thumbnail_widgets.append(widget)

    def set_controls_enabled(self, enabled):
        self.btn_select_file.setEnabled(enabled)
        self.btn_select_folder.setEnabled(enabled)
        self.btn_select_zip.setEnabled(enabled)
        self.btn_convert.setEnabled(enabled)
        if enabled:
            self.progress_bar.setTextVisible(False)

    def closeEvent(self, event):
        self.controller.cancel_conversion()
        self.clear_thumbnails() # Limpiar miniaturas al cerrar
        event.accept()

def convertir_docx_a_pdf(docx_path, output_dir):
    pdf_path = os.path.join(output_dir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
    comtypes.CoInitialize()
    word = comtypes.client.CreateObject('Word.Application')
    word.Visible = False
    doc = word.Documents.Open(docx_path)
    doc.SaveAs(pdf_path, FileFormat=17)  # 17 = wdFormatPDF
    doc.Close()
    word.Quit()
    return pdf_path