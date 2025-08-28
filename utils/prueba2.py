import os
import re
import unicodedata
import difflib
from Models.validation_model import EXPEDIENTE_STRUCTURE

class ValidationService:
    def __init__(self):
        self.report_lines = []

    # ===================== Helpers de normalización y matching =====================

    def _normalize_name(self, name):
        """
        Normaliza un nombre de archivo/carpeta para comparación flexible:
        - minúsculas
        - quita tildes
        - quita prefijos numéricos: '01.', '2_', '3-'
        - elimina espacios, puntos, guiones y underscores
        """
        name = name.lower()
        name = ''.join(
            c for c in unicodedata.normalize('NFD', name)
            if unicodedata.category(c) != 'Mn'
        )
        name = re.sub(r'^\d+[\s._-]*', '', name)
        name = re.sub(r'[\s._-]+', '', name)
        return name

    def _find_match(self, name_to_find, items_in_dir):
        """
        Busca un elemento (archivo o carpeta) en items_in_dir con tolerancia:
        - Coincidencia exacta tras normalizar
        - Coincidencia aproximada (fuzzy >= 0.8)
        Devuelve el nombre original si encuentra, o None.
        """
        normalized_to_find = self._normalize_name(name_to_find)
        normalized_items = {self._normalize_name(item): item for item in items_in_dir}

        if normalized_to_find in normalized_items:
            return normalized_items[normalized_to_find]

        close = difflib.get_close_matches(normalized_to_find, normalized_items.keys(), n=1, cutoff=0.8)
        if close:
            return normalized_items[close[0]]

        return None

    def _match_file_alias(self, alias, items_in_dir):
        """
        Coincide archivos por alias:
        - Soporta comodín tipo '*.sp3' (acepta cualquier nombre con esa extensión)
        - Soporta coincidencia flexible por nombre (ignorando separadores/tildes/mayús)
        - Insensible a la extensión en mayúsculas/minúsculas
        """
        alias = alias.lower()
        alias_base, alias_ext = os.path.splitext(alias)

        # Caso comodín por extensión: '*.sp3', '*.PDF', etc.
        # if '*' in alias and alias_ext:
        #     for item in items_in_dir:
        #         if not os.path.isfile(os.path.join(self._current_dir, item)):
        #             continue
        #         if os.path.splitext(item)[1].lower() == alias_ext:
        #             return item
        #     return None

        if '*' in alias and alias_ext:
            for item in items_in_dir:
                if not os.path.isfile(os.path.join(self._current_dir, item)):
                    continue
                # Normaliza extensión completa, incluyendo .sp3 y .sp3.gz
                if item.lower().endswith(alias_ext):
                    return item
            return None

        # Caso sin comodín: usar _find_match para el "base" y validar extensión si se especificó
        match = self._find_match(alias_base, items_in_dir)
        if not match:
            return None

        if alias_ext:
            if os.path.splitext(match)[1].lower() != alias_ext:
                return None
        return match

    # ===================== Validación recursiva =====================

    def _check_folder(self, dir_path, folder_struct, optional_items, indent=""):
        """
        Valida una carpeta contra su estructura (folder_struct) y sus hijos.
        Además, maneja reglas dinámicas (puntos geodésicos) si están habilitadas.
        """
        if not os.path.isdir(dir_path):
            return

        # Guardar directorio actual (para _match_file_alias)
        self._current_dir = dir_path
        items_in_dir = os.listdir(dir_path)

        # 1) Validar elementos definidos explícitamente en el modelo
        known_children_norm_aliases = set()
        for item_struct in folder_struct.get("children", []):
            item_name = item_struct["name"]
            is_optional = item_struct["optional"]
            item_type = item_struct["type"]

            # Para exclusión de dinámicos: registrar aliases/nombre oficial
            for a in item_struct.get("aliases", []) + [item_name]:
                known_children_norm_aliases.add(self._normalize_name(a))

            # Si es opcional y no fue seleccionado en la UI, omitir
            if is_optional and item_name not in optional_items:
                self.report_lines.append(f"{indent}[Omitido] {item_name}")
                continue

            found_item_name = None

            if item_type == "file":
                # Probar cada alias (incluye manejo de comodín)
                for alias in item_struct.get("aliases", []):
                    found_item_name = self._match_file_alias(alias, items_in_dir)
                    if found_item_name:
                        break
                # Si no encontró por alias, intento final por nombre exacto (flexible)
                if not found_item_name:
                    found_item_name = self._match_file_alias(item_name, items_in_dir)

            else:  # folder
                # Buscar por cualquiera de los aliases (o por el nombre oficial)
                for alias in item_struct.get("aliases", []) + [item_name]:
                    found_item_name = self._find_match(alias, items_in_dir)
                    if found_item_name and os.path.isdir(os.path.join(dir_path, found_item_name)):
                        break
                # Si por alguna razón coincidió con un archivo, ignorar
                if found_item_name and not os.path.isdir(os.path.join(dir_path, found_item_name)):
                    found_item_name = None

            # Reporte + recursión
            if found_item_name:
                self.report_lines.append(f"{indent}[✓] Encontrado: {item_name} (como '{found_item_name}')")
                if item_type == "folder" and item_struct.get("children"):
                    self._check_folder(os.path.join(dir_path, found_item_name), item_struct, optional_items, indent + "    ")
            else:
                status = "[!] Faltante:" if not is_optional else "[i] Faltante (Opcional):"
                self.report_lines.append(f"{indent}{status} {item_name}")

        # 2) Reglas dinámicas: carpetas de puntos dentro de DATOS_GNSS
        if folder_struct.get("allow_dynamic_points", False):
            self._check_dynamic_point_folders(dir_path, items_in_dir, known_children_norm_aliases, indent)

    def _check_dynamic_point_folders(self, dir_path, items_in_dir, known_children_norm_aliases, indent):
        """
        Detecta carpetas adicionales (no definidas en el modelo) dentro de DATOS_GNSS y
        las valida como posibles [CODIGO_PUNTO_GEODESICO] exigiendo subcarpetas Nativo y RINEX.
        """
        unknown_point_dirs = []
        for item in items_in_dir:
            full = os.path.join(dir_path, item)
            if not os.path.isdir(full):
                continue
            norm = self._normalize_name(item)
            if norm not in known_children_norm_aliases:
                unknown_point_dirs.append(item)

        if not unknown_point_dirs:
            # Si quieres que no imprima nada cuando no hay puntos, comenta la línea de abajo
            self.report_lines.append(f"{indent}[i] No se detectaron carpetas adicionales de puntos geodésicos.")
            return

        for point_dir in unknown_point_dirs:
            self.report_lines.append(f"{indent}[✓] Carpeta de punto detectada: '{point_dir}'")
            sub_path = os.path.join(dir_path, point_dir)
            sub_items = os.listdir(sub_path)

            # Validar subcarpetas requeridas
            required_subfolders = ["Nativo", "RINEX"]
            for req in required_subfolders:
                found = self._find_match(req, sub_items)
                if found and os.path.isdir(os.path.join(sub_path, found)):
                    self.report_lines.append(f"{indent}    [✓] Subcarpeta '{req}' encontrada (como '{found}')")
                else:
                    self.report_lines.append(f"{indent}    [!] Faltante: subcarpeta '{req}'")

    # ===================== Público =====================

    def validate_expediente(self, root_path, optional_items_to_check):
        self.report_lines = []
        self.report_lines.append("--- INICIO DEL REPORTE DE VALIDACIÓN ---")
        self.report_lines.append(f"Expediente analizado: {root_path}\n")

        # Validar desde la raíz del modelo
        self._check_folder(root_path, EXPEDIENTE_STRUCTURE, optional_items_to_check)

        self.report_lines.append("\n--- FIN DEL REPORTE ---")
        return "\n".join(self.report_lines)



# # GUI/validation_view.py
# import os
# from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
#                              QLineEdit, QFileDialog, QTextEdit, QCheckBox, QScrollArea,
#                              QMessageBox, QGroupBox)
# from PyQt5.QtCore import Qt
# from Controllers.validation_controller import ValidationController
# from Models.validation_model import EXPEDIENTE_STRUCTURE

# class ValidationView(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.controller = ValidationController(self)
#         self.optional_checkboxes = {}
#         self.init_ui()

#     def init_ui(self):
#         self.setWindowTitle("Validador de Expediente de Certificación")
#         self.setMinimumSize(800, 600)

#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(20, 20, 20, 20)
#         main_layout.setSpacing(15)

#         # 1. Selección de Carpeta
#         folder_layout = QHBoxLayout()
#         self.path_line_edit = QLineEdit()
#         self.path_line_edit.setPlaceholderText("Seleccione la carpeta del expediente...")
#         self.path_line_edit.setReadOnly(True)
#         btn_browse = QPushButton("Seleccionar Carpeta...")
#         btn_browse.clicked.connect(self.select_folder)
#         folder_layout.addWidget(self.path_line_edit)
#         folder_layout.addWidget(btn_browse)
#         main_layout.addLayout(folder_layout)

#         # 2. Opciones de Validación (Checkboxes para items opcionales)
#         options_group = QGroupBox("Elementos Opcionales a Validar")
#         scroll = QScrollArea()
#         scroll.setWidgetResizable(True)
#         scroll_content = QWidget()
#         self.options_layout = QVBoxLayout(scroll_content)
        
#         self._populate_optional_items(EXPEDIENTE_STRUCTURE['children'])

#         scroll.setWidget(scroll_content)
#         options_group_layout = QVBoxLayout()
#         options_group_layout.addWidget(scroll)
#         options_group.setLayout(options_group_layout)
#         main_layout.addWidget(options_group)

#         # 3. Botones de Acción
#         action_layout = QHBoxLayout()
#         btn_validate = QPushButton("Iniciar Validación")
#         btn_validate.clicked.connect(self.start_validation)
#         self.btn_save_report = QPushButton("Guardar Reporte")
#         self.btn_save_report.setEnabled(False)
#         self.btn_save_report.clicked.connect(self.save_report)
#         action_layout.addStretch()
#         action_layout.addWidget(btn_validate)
#         action_layout.addWidget(self.btn_save_report)
#         main_layout.addLayout(action_layout)

#         # 4. Área de Resultados
#         self.results_text_edit = QTextEdit()
#         self.results_text_edit.setReadOnly(True)
#         self.results_text_edit.setFontFamily("Courier New")
#         main_layout.addWidget(self.results_text_edit)

#     def _populate_optional_items(self, structure):
#         """ Llena recursivamente los checkboxes de items opcionales. """
#         for item in structure:
#             if item['optional']:
#                 checkbox = QCheckBox(item['name'])
#                 checkbox.setChecked(True) # Por defecto marcados
#                 self.options_layout.addWidget(checkbox)
#                 self.optional_checkboxes[item['name']] = checkbox
#             if item['children']:
#                 self._populate_optional_items(item['children'])

#     def select_folder(self):
#         folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta Raíz del Expediente")
#         if folder:
#             self.path_line_edit.setText(folder)

#     def start_validation(self):
#         root_path = self.path_line_edit.text()
#         if not root_path or not os.path.isdir(root_path):
#             QMessageBox.warning(self, "Carpeta no válida", "Por favor, seleccione una carpeta de expediente válida.")
#             return
        
#         # Obtener los items opcionales seleccionados
#         selected_optionals = {name for name, cb in self.optional_checkboxes.items() if cb.isChecked()}
        
#         self.controller.start_validation(root_path, selected_optionals)

#     def save_report(self):
#         report_content = self.results_text_edit.toPlainText()
#         if not report_content:
#             QMessageBox.warning(self, "Sin Contenido", "No hay reporte para guardar.")
#             return
        
#         file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte", "", "Archivos de Texto (*.txt)")
#         if file_path:
#             self.controller.save_report(file_path, report_content)

#     def show_results(self, report_text):
#         self.results_text_edit.setText(report_text)
#         self.btn_save_report.setEnabled(True)

#     def show_message(self, title, message, level="info"):
#         if level == "info":
#             QMessageBox.information(self, title, message)
#         elif level == "warning":
#             QMessageBox.warning(self, title, message)
#         elif level == "error":
#             QMessageBox.critical(self, title, message)

