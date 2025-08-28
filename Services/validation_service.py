
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
        - Soporta comodín tipo '*.sp3' o '*.sp3.gz' (acepta cualquier archivo con esa extensión, case-insensitive)
        - Soporta coincidencia flexible por nombre (sin comodín)
        - Insensible a la extensión en mayúsculas/minúsculas
        """
        alias = alias.lower()

        # Caso comodín: '*.sp3', '*.sp3.gz', etc.
        if '*' in alias:
            matches = []
            suffix = alias.replace('*', '')  # '.sp3' o '.sp3.gz'
            for item in items_in_dir:
                fullp = os.path.join(self._current_dir, item)
                if not os.path.isfile(fullp):
                    continue
                if item.lower().endswith(suffix):
                    matches.append(item)
            return matches if matches else None

        # Caso sin comodín: usar _find_match para el "base" y validar extensión si se especificó
        alias_base, alias_ext = os.path.splitext(alias)
        match = self._find_match(alias_base, items_in_dir)
        if not match:
            return None

        if alias_ext:
            if not match.lower().endswith(alias_ext):
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
        try:
            items_in_dir = os.listdir(dir_path)
        except OSError:
            items_in_dir = []

        # matched sets para evitar reportes dobles como "no esperado"
        matched_items = set()        # nombres reales tal cual en FS que ya fueron reconocidos
        matched_norms = set()        # normalizados de los items reconocidos
        matched_file_bases_norm = set()  # bases normalizadas de archivos reconocidos (evita carpetas con mismo base)

        # 1) Validar elementos definidos explícitamente en el modelo
        known_children_norm_aliases = set()
        wildcard_exts = set()
        for item_struct in folder_struct.get("children", []):
            # registrar aliases/nombre oficial (normalizados)
            for a in item_struct.get("aliases", []) + [item_struct["name"]]:
                known_children_norm_aliases.add(self._normalize_name(a))

            # si es file, también registrar la 'base' (sin extensión) normalizada para comparación
            if item_struct.get("type") == "file":
                base = os.path.splitext(item_struct["name"])[0]
                known_children_norm_aliases.add(self._normalize_name(base))
                for a in item_struct.get("aliases", []):
                    if "*" in a:
                        # guardar sufijo esperado (ej '.sp3' o '.sp3.gz') para heurísticas
                        wildcard_exts.add(a.replace('*', '').lower())
                    else:
                        known_children_norm_aliases.add(self._normalize_name(os.path.splitext(a)[0]))

        for item_struct in folder_struct.get("children", []):
            item_name = item_struct["name"]
            is_optional = item_struct.get("optional", False)
            item_type = item_struct.get("type")

            # Si es opcional y no fue seleccionado en la UI, omitir
            if is_optional and item_name not in optional_items:
                self.report_lines.append(f"{indent}[Omitido] {item_name}")
                continue

            found_item_name = None

            if item_type == "file":
                # Probar cada alias (incluye manejo de comodín)
                found_matches = None
                for alias in item_struct.get("aliases", []):
                    found = self._match_file_alias(alias, items_in_dir)
                    if found:
                        found_matches = found
                        break
                # Si no encontró por alias, intento final por nombre exacto (flexible)
                if not found_matches:
                    found = self._match_file_alias(item_name, items_in_dir)
                    if found:
                        found_matches = found

                # Reporte de archivos encontrados
                if found_matches:
                    # matched_matches puede ser lista (comodín) o string (single)
                    if isinstance(found_matches, list):
                        for f in found_matches:
                            # reportar solo si no fue reportado antes en este folder
                            if f not in matched_items:
                                self.report_lines.append(f"{indent}[✓] Encontrado: {item_name} (como '{f}')")
                                matched_items.add(f)
                                matched_norms.add(self._normalize_name(f))
                                # base sin extension (una retirada de una sola ext, ej .gz)
                                base = os.path.splitext(f)[0]
                                matched_file_bases_norm.add(self._normalize_name(base))
                    else:
                        f = found_matches
                        if f not in matched_items:
                            self.report_lines.append(f"{indent}[✓] Encontrado: {item_name} (como '{f}')")
                            matched_items.add(f)
                            matched_norms.add(self._normalize_name(f))
                            base = os.path.splitext(f)[0]
                            matched_file_bases_norm.add(self._normalize_name(base))
                else:
                    status = "[!] Faltante:" if not is_optional else "[i] Faltante (Opcional):"
                    self.report_lines.append(f"{indent}{status} {item_name}")

            else:  # folder
                # Buscar por cualquiera de los aliases (o por el nombre oficial)
                found_item_name = None
                for alias in item_struct.get("aliases", []) + [item_name]:
                    candidate = self._find_match(alias, items_in_dir)
                    if candidate and os.path.isdir(os.path.join(dir_path, candidate)):
                        found_item_name = candidate
                        break

                # Si por alguna razón coincidió con un archivo, ignorar
                if found_item_name and not os.path.isdir(os.path.join(dir_path, found_item_name)):
                    found_item_name = None

                # Reporte + recursión
                if found_item_name:
                    self.report_lines.append(f"{indent}[✓] Encontrado: {item_name} (como '{found_item_name}')")
                    matched_items.add(found_item_name)
                    matched_norms.add(self._normalize_name(found_item_name))
                    if item_struct.get("children"):
                        self._check_folder(os.path.join(dir_path, found_item_name), item_struct, optional_items, indent + "    ")
                else:
                    status = "[!] Faltante:" if not is_optional else "[i] Faltante (Opcional):"
                    self.report_lines.append(f"{indent}{status} {item_name}")

        # 2) Reglas dinámicas: carpetas de puntos dentro de DATOS_GNSS
        if folder_struct.get("allow_dynamic_points", False):
            # actualizar matched_items desde la función dinámica
            self._check_dynamic_point_folders(dir_path, items_in_dir, known_children_norm_aliases, indent, matched_items, matched_norms, matched_file_bases_norm)

        # 3) Detectar carpetas/archivos no esperados
        IGNORED = {".ds_store", "thumbs.db", "desktop.ini"}
        for item in items_in_dir:
            low = item.lower()
            if low in IGNORED:
                continue
            norm = self._normalize_name(item)

            # si ya fue reconocido explícitamente, no lo marcamos como inesperado
            if norm in known_children_norm_aliases or norm in matched_norms:
                continue

            # si es carpeta y su nombre normalizado coincide con la base de un archivo match (ej. SP3 carpeta vs .sp3.gz archivo), ignorar
            full_path = os.path.join(dir_path, item)
            if os.path.isdir(full_path):
                base_norm = self._normalize_name(os.path.splitext(item)[0])
                if base_norm in matched_file_bases_norm:
                    continue

            # si es archivo y su extension coincide con un wildcard esperado (pero no fue reportado), lo consideramos ya 'matched' y lo saltamos
            if os.path.isfile(full_path):
                low_item = item.lower()
                matched_by_wildcard = any(low_item.endswith(sfx) for sfx in wildcard_exts)
                if matched_by_wildcard:
                    # marcar en matched (evita reportarlo)
                    matched_items.add(item)
                    matched_norms.add(norm)
                    continue

            # Si no cumple ninguna de las condiciones anteriores, lo reportamos como inesperado
            if os.path.isdir(full_path):
                self.report_lines.append(f"{indent}[?] Carpeta no esperada: '{item}'")
            else:
                self.report_lines.append(f"{indent}[?] Archivo no esperado: '{item}'")

    def _check_dynamic_point_folders(self, dir_path, items_in_dir, known_children_norm_aliases, indent, matched_items, matched_norms, matched_file_bases_norm):
        """
        Detecta carpetas adicionales (no definidas en el modelo) dentro de DATOS_GNSS y
        las valida como posibles [CODIGO_PUNTO_GEODESICO] exigiendo subcarpetas Nativo y RINEX.
        Al detectarlas las añade a matched_items/matched_norms para que no se marquen luego como inesperadas.
        """
        unknown_point_dirs = []
        for item in items_in_dir:
            full = os.path.join(dir_path, item)
            if not os.path.isdir(full):
                continue
            norm = self._normalize_name(item)
            if norm not in known_children_norm_aliases and norm not in matched_norms:
                unknown_point_dirs.append(item)

        if not unknown_point_dirs:
            self.report_lines.append(f"{indent}[i] No se detectaron carpetas adicionales de puntos geodésicos.")
            return

        for point_dir in unknown_point_dirs:
            # marcar como reconocido
            matched_items.add(point_dir)
            matched_norms.add(self._normalize_name(point_dir))

            self.report_lines.append(f"{indent}[✓] Carpeta de punto detectada: '{point_dir}'")
            sub_path = os.path.join(dir_path, point_dir)
            try:
                sub_items = os.listdir(sub_path)
            except OSError:
                sub_items = []

            # Validar subcarpetas requeridas
            required_subfolders = ["Nativo", "RINEX"]
            for req in required_subfolders:
                found = self._find_match(req, sub_items)
                if found and os.path.isdir(os.path.join(sub_path, found)):
                    self.report_lines.append(f"{indent}    [✓] Subcarpeta '{req}' encontrada (como '{found}')")
                    # añadir subcarpeta encontrada al matched (relativa al punto)
                    matched_norms.add(self._normalize_name(found))
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
