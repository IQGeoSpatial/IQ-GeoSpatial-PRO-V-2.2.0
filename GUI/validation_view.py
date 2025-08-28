
import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QCheckBox, QMessageBox
)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QIcon, QFont
from PyQt5.QtCore import Qt, QSize
from Controllers.validation_controller import ValidationController
from Models.validation_model import EXPEDIENTE_STRUCTURE
from utils.resource_path import resource_path


class ValidationView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = ValidationController(self)
        self.optional_checkboxes = {}
        # Subcadenas para identificar checkboxes a excluir (flexibles)
        self.excluded_substrings = [
            "certificado punto de base",
            "sustento de altura de antena"
        ]
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Validador de Expediente de Certificación")
        self.setWindowIcon(QIcon(resource_path(os.path.join("Assets", "Image", "file_check.png"))))
        self.setMinimumSize(820, 670)

        # === Fondo de ventana ===
        bg_pixmap = QPixmap(resource_path(os.path.join("Assets", "Image", "file_check.png")))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(bg_pixmap.scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
        self.setPalette(palette)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # === Botón central para cargar carpeta ===
        self.btn_browse = QPushButton()
        self.btn_browse.setIcon(QIcon(resource_path(os.path.join("Assets", "Image", "file_check.png"))))
        self.btn_browse.setIconSize(QSize(100, 100))
        self.btn_browse.setFixedSize(120, 120)
        self.btn_browse.setStyleSheet("background-color: transparent; border: none;")
        self.btn_browse.clicked.connect(self.select_folder)

        browse_layout = QVBoxLayout()
        browse_layout.setSpacing(8)
        browse_layout.addWidget(self.btn_browse, alignment=Qt.AlignCenter)

        browse_label = QLabel("Cargar Expediente")
        browse_label.setAlignment(Qt.AlignCenter)
        browse_label.setFont(QFont("Arial", 12))
        browse_layout.addWidget(browse_label)

        # Separación extra para que las etiquetas estén más abajo
        browse_layout.addSpacing(15)

        self.folder_name_label = QLabel("")
        self.folder_name_label.setAlignment(Qt.AlignCenter)
        self.folder_name_label.setFont(QFont("Arial", 12, QFont.Bold))

        self.folder_path_label = QLabel("")
        self.folder_path_label.setAlignment(Qt.AlignCenter)
        self.folder_path_label.setFont(QFont("Arial", 12))

        browse_layout.addWidget(self.folder_name_label)
        browse_layout.addWidget(self.folder_path_label)

        main_layout.addLayout(browse_layout)

        # === Opciones de Validación (en fila) ===
        options_layout = QHBoxLayout()
        options_layout.addStretch()

        self.optional_checkboxes = {}
        self._populate_optional_items(EXPEDIENTE_STRUCTURE['children'], options_layout)

        options_layout.addStretch()
        main_layout.addLayout(options_layout)

        # === Botones de acción ===
        action_layout = QHBoxLayout()
        btn_validate = QPushButton("Iniciar Validación")
        btn_validate.setFont(QFont("Arial", 12))
        btn_validate.clicked.connect(self.start_validation)

        self.btn_save_report = QPushButton("")
        self.btn_save_report.setEnabled(False)
        self.btn_save_report.setIcon(QIcon(resource_path(os.path.join("Assets", "Image", "guardar.png"))))
        self.btn_save_report.setIconSize(QSize(27, 27))
        self.btn_save_report.setStyleSheet("background-color: transparent; border: none;")
        self.btn_save_report.clicked.connect(self.save_report)

        action_layout.addStretch()
        action_layout.addWidget(btn_validate)
        action_layout.addWidget(self.btn_save_report)
        main_layout.addLayout(action_layout)

        # === Área de resultados ===
        self.results_text_edit = QTextEdit()
        self.results_text_edit.setReadOnly(True)
        self.results_text_edit.setFont(QFont("Consolas", 12))
        self.results_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2f;
                color: #f8f8f2;
                font-family: Consolas, Courier, monospace;
                font-size: 10pt;
                border: 2px solid #444;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        main_layout.addWidget(self.results_text_edit)

    def _populate_optional_items(self, structure, layout):
        """ Llena recursivamente los checkboxes de items opcionales. """
        for item in structure:
            if item['optional']:
                name_lower = item['name'].strip().lower()
                # Excluir si contiene cualquiera de las subcadenas definidas
                is_excluded = any(sub in name_lower for sub in self.excluded_substrings)

                if not is_excluded:
                    clean_name = item['name'].strip()
                    checkbox = QCheckBox(clean_name)
                    checkbox.setChecked(True)
                    checkbox.setFont(QFont("Arial", 12))
                    layout.addWidget(checkbox)
                    self.optional_checkboxes[clean_name] = checkbox
            
            if item['children']:
                self._populate_optional_items(item['children'], layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta Raíz del Expediente")
        if folder:
            self.folder_name_label.setText(os.path.basename(folder))
            self.folder_path_label.setText(folder)

    def start_validation(self):
        root_path = self.folder_path_label.text()
        if not root_path or not os.path.isdir(root_path):
            QMessageBox.warning(self, "Carpeta no válida", "Por favor, seleccione una carpeta de expediente válida.")
            return

        selected_optionals = {name for name, cb in self.optional_checkboxes.items() if cb.isChecked()}
        self.controller.start_validation(root_path, selected_optionals)

    def save_report(self):
        report_content = self.results_text_edit.toPlainText()
        if not report_content:
            QMessageBox.warning(self, "Sin Contenido", "No hay reporte para guardar.")
            return

        folder_name = self.folder_name_label.text()
        if folder_name:
            default_filename = f"Reporte de Validación - {folder_name}.txt"
        else:
            default_filename = "Reporte de Validación.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Reporte", default_filename, "Archivos de Texto (*.txt)")
        if file_path:
            self.controller.save_report(file_path, report_content)

    def show_results(self, report_text):
        self.results_text_edit.setText(report_text)
        self.btn_save_report.setEnabled(True)

    def show_message(self, title, message, level="info"):
        if level == "info":
            QMessageBox.information(self, title, message)
        elif level == "warning":
            QMessageBox.warning(self, title, message)
        elif level == "error":
            QMessageBox.critical(self, title, message)