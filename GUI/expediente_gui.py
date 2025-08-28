"""
/***************************************************************************
 IQ GeoSpatial
             Folder structure for Geodetic Point Certification
             Downloads Efemerides ESA
             Creating Forms

                ------------------------------------------
        begin                : 2025-08-06
        git sha              : $Format:%H$
        copyright            : (C) 2025 by IQ GeoSpatial
        email                : iqgeospatial@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import shutil
import tempfile
import folium, tempfile
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QMessageBox, QProgressBar, QSpacerItem, QSizePolicy, QFileDialog, QGridLayout, QComboBox, QGroupBox, QCalendarWidget, QDialogButtonBox, QDialog, QScrollArea, QToolTip, QTableWidget, QTableWidgetItem, QHeaderView, QApplication, QInputDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QSize, QRect, Qt, QTimer
import pandas as pd, tempfile
from PyQt5.QtWidgets import QFrame

from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor, QPen, QBrush, QFont

from utils.resource_path import resource_path
from utils.map_utils import este_norte_a_latlon
from Models.DataBase import CodigoDB
from Models.Expediente_models import ExpedienteModel
from Controllers.expediente_controller import ExpedienteController
from utils.licencia_utils import puede_usar_app, registrar_uso, ingresar_licencia
from GUI.licencia_dialog import LicenciaDialog

# Estilo de Mensajes Emergentes
def mostrar_mensaje(parent, titulo, texto, icono=QMessageBox.Information):
    msg = QMessageBox(parent)
    msg.setIcon(icono)
    msg.setText(texto)
    msg.setWindowTitle(titulo)
    msg.setStyleSheet("""
        
        QLabel {
            color: #b0b0b0;
            background: none;
        }
    """)
    msg.exec_()    

class FechasButton(QPushButton):
    def __init__(self, parent, get_num_dias):
        super().__init__("Fechas", parent)
        self.get_num_dias = get_num_dias

    def enterEvent(self, event):
        if int(self.get_num_dias()) == 1:
            QToolTip.showText(
                self.mapToGlobal(self.rect().bottomLeft()),
                "Este campo es solo para días superiores\n a 1 día de lectura. Si es 1,\n la fecha se crea automáticamente.",
                self
            )
        else:
            QToolTip.hideText()
        super().enterEvent(event)

class ImageViewerDialog(QDialog):
    # Diccionario a nivel de clase para guardar el estado (zoom, pan) de cada imagen
    image_states = {}

    def cambiar_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar nueva imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)")
        if ruta:
            self.image_path = ruta
            self.pixmap = QPixmap(self.image_path)
            self.image_label.setPixmap(self.pixmap)
            self.image_label.update()
            self.image_label.fit_to_window()
            # Actualiza el botón de la tabla inmediatamente
            if self.sender_button and hasattr(self.sender_button, 'setProperty'):
                self.sender_button.setProperty("image_path", ruta)
                self.sender_button.setIcon(QIcon(ruta))
                self.sender_button.setIconSize(QSize(32, 32))

    def accept(self):
        # Al cerrar el diálogo, actualiza el botón original con la nueva imagen
        if self.sender_button and hasattr(self, 'image_path') and os.path.exists(self.image_path):
            # Busca el método update_button_image en el parent (DialogoFormularios)
            parent = self.parent()
            if parent and hasattr(parent, 'update_button_image'):
                parent.update_button_image(self.sender_button, self.image_path)
        super().accept()
    """Un diálogo para mostrar una imagen con zoom y pan."""


    def __init__(self, image_path, sender_button, parent=None, tipo_imagen=None):
        super().__init__(parent)
        self.setWindowTitle(os.path.basename(image_path))
        self.setFixedSize(700, 600)
        self.sender_button = sender_button
        self.setStyleSheet("background-color: #f0f0f0;")

        self.image_path = image_path
        self.pixmap = QPixmap(image_path)
        self.panning = False
        self.last_mouse_pos = None

        # --- UI Setup ---

        self.scroll_area = QScrollArea()
        visible_w = 700
        visible_h = 600
        canvas_w = visible_w * 5
        canvas_h = visible_h * 5
        self.canvas = QWidget()
        self.canvas.setMinimumSize(canvas_w, canvas_h)
        self.canvas.setStyleSheet("background: #f0f0f0;")
        self.image_label = PreviewImageLabel(self.pixmap, scroll_area=self.scroll_area, canvas=self.canvas)
        self.image_label.setParent(self.canvas)
        self.img_start_x = canvas_w // 2 - self.pixmap.width() // 2
        self.img_start_y = canvas_h // 2 - self.pixmap.height() // 2
        self.image_label.move(self.img_start_x, self.img_start_y)
        QTimer.singleShot(0, self.restore_or_center_view)

        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("background: #f0f0f0;")

        # Dimensiones por tipo de imagen
        dimensiones = {
            "UBICACION PG": (9.7, 10.1),
            "POSICIONAMIENTO GPS-GNSS": (5.5, 4.5),
            "DISCO DE BRONCE": (5.5, 4.5),
            "ALTURA DE ANTENA": (8.5, 10.1)
        }
        if tipo_imagen in dimensiones:
            width_cm, height_cm = dimensiones[tipo_imagen]
        else:
            width_cm, height_cm = 8.5, 9 # Default

        # Overlay widget para el marco estático
        for child in self.scroll_area.viewport().findChildren(StaticFrameOverlay):
            child.setParent(None)
            child.deleteLater()
        self.overlay_frame = StaticFrameOverlay(self.scroll_area.viewport(), width_cm=width_cm, height_cm=height_cm, dpi=96)
        self.overlay_frame.setGeometry(0, 0, self.scroll_area.viewport().width(), self.scroll_area.viewport().height())
        self.overlay_frame.raise_()
        self.overlay_frame.show()

        action_layout = QHBoxLayout()
        action_layout.setAlignment(Qt.AlignCenter)
        action_layout.setSpacing(20)
        self.btn_cambiar = QPushButton("Cambiar imagen")
        self.btn_cambiar.setStyleSheet("background: #3498db; color: white; border: none; border-radius: 5px; font-size: 12px; font-weight: bold; padding: 8px;")
        self.btn_cambiar.clicked.connect(self.cambiar_imagen)
        action_layout.addWidget(self.btn_cambiar)
        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
        layout.addLayout(action_layout)
        self.setLayout(layout)
        self.scroll_area.viewport().installEventFilter(self.overlay_frame)

    def restore_or_center_view(self):
        """Restaura la posición y el zoom guardados, o centra la imagen si es la primera vez que se abre."""
        if self.image_path in ImageViewerDialog.image_states:
            # Restaurar estado guardado
            state = ImageViewerDialog.image_states[self.image_path]
            self.image_label.scale_factor = state['scale']
            self.image_label.update_image_scale()
            self.scroll_area.horizontalScrollBar().setValue(state['h_scroll'])
            self.scroll_area.verticalScrollBar().setValue(state['v_scroll'])
        else:
            # Comportamiento por defecto: centrar y mostrar en tamaño real
            self.image_label.show_original_size()
            h_val = self.img_start_x - (self.scroll_area.viewport().width() // 2 - self.pixmap.width() // 2)
            v_val = self.img_start_y - (self.scroll_area.viewport().height() // 2 - self.pixmap.height() // 2)
            self.scroll_area.horizontalScrollBar().setValue(h_val)
            self.scroll_area.verticalScrollBar().setValue(v_val)

    def closeEvent(self, event):
        """Guarda el estado actual (zoom y pan) antes de cerrar el diálogo."""
        state = {'scale': self.image_label.scale_factor, 'h_scroll': self.scroll_area.horizontalScrollBar().value(), 'v_scroll': self.scroll_area.verticalScrollBar().value()}
        ImageViewerDialog.image_states[self.image_path] = state
        super().closeEvent(event)

    def recortar_y_guardar(self):
        """Captura el área dentro del marco rojo, la guarda en un archivo temporal y actualiza la ruta."""
        try:
            # 1. Obtener el rectángulo de recorte del overlay
            crop_rect = self.overlay_frame.get_frame_rect()

            # 2. Capturar el contenido del viewport del scroll_area
            viewport_pixmap = self.scroll_area.viewport().grab()

            # 3. Recortar la imagen capturada
            cropped_pixmap = viewport_pixmap.copy(crop_rect)

            # 4. Guardar en un archivo temporal
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False, prefix="recorte_") as temp_file:
                temp_path = temp_file.name
            cropped_pixmap.save(temp_path)

            # 5. Actualizar la propiedad 'image_path' del botón original en la tabla
            if self.sender_button:
                self.sender_button.setProperty("image_path", temp_path)
                # print(f"[DEBUG] Ruta de imagen actualizada a: {temp_path}")

            QMessageBox.information(self, "Éxito", f"Recorte guardado temporalmente.\nLa nueva ruta se usará al generar el formulario.")
            self.accept() # Cierra el diálogo

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo procesar el recorte: {e}")

class StaticFrameOverlay(QWidget):
    def __init__(self, parent, width_cm=8.5, height_cm=9, dpi=96):
        super().__init__(parent)        
        self.frame_width_cm = width_cm
        self.frame_height_cm = height_cm
        self.dpi = dpi
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setStyleSheet("background: transparent;")
        self.resize(parent.size())
        parent.installEventFilter(self)

    def eventFilter(self, obj, event):
        # Mantener el overlay siempre del tamaño del viewport
        if event.type() == event.Resize:
            self.setGeometry(0, 0, obj.width(), obj.height())
        return False

    def get_frame_rect(self):
        """Calcula y devuelve el rectángulo del marco en píxeles."""
        px_per_cm = self.dpi / 2.54
        frame_w = int(self.frame_width_cm * px_per_cm)
        frame_h = int(self.frame_height_cm * px_per_cm)
        x = (self.width() - frame_w) // 2
        y = (self.height() - frame_h) // 2
        return QRect(x, y, frame_w, frame_h)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.get_frame_rect()
        x, y, frame_w, frame_h = rect.x(), rect.y(), rect.width(), rect.height()
        # Overlay semitransparente fuera del marco
        overlay_color = QColor(0, 0, 0, 100)
        painter.setBrush(QBrush(overlay_color))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, self.width(), y)
        painter.drawRect(0, y + frame_h, self.width(), self.height() - (y + frame_h))
        painter.drawRect(0, y, x, frame_h)
        painter.drawRect(x + frame_w, y, self.width() - (x + frame_w), frame_h)
        # Marco visible
        pen = QPen(QColor(255, 0, 0, 180), 3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(rect)
        # Texto de dimensiones en negro y negrita
        font = QFont()
        font.setBold(True)
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(x + 8, y + 25, f"{self.frame_width_cm} x {self.frame_height_cm} cm")
        painter.end()

    def cambiar_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar nueva imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)")
        if ruta:
            self.image_path = ruta
            self.pixmap = QPixmap(self.image_path)
            self.image_label.setPixmap(self.pixmap)
            self.image_label.update()
            self.image_label.fit_to_window()

# --- Widget personalizado para mostrar overlay de marco de inserción ---

class PreviewImageLabel(QLabel):
    def show_original_size(self):
        """Muestra la imagen en su tamaño real (zoom 100%)."""
        if self._original_pixmap is None or self._original_pixmap.isNull():
            return
        self.scale_factor = 1.0
        self.setPixmap(self._original_pixmap)
        self.resize(self._original_pixmap.size())
    def __init__(self, pixmap, parent=None, scroll_area=None, canvas=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self._original_pixmap = QPixmap(pixmap) if pixmap is not None else None
        self.setPixmap(self._original_pixmap)
        self.setMinimumSize(20, 20)
        self.scroll_area = scroll_area
        self.canvas = canvas
        self.scale_factor = 1.0
        self._min_scale = 0.25  # 25% del tamaño real
        self._max_scale = 1.5   # 150% del tamaño real

    # El overlay ya no se dibuja aquí, solo la imagen
    def paintEvent(self, event):
        super().paintEvent(event)
    def cambiar_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Seleccionar nueva imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)")
        if ruta:
            self.image_path = ruta
            self._original_pixmap = QPixmap(self.image_path)
            self.scale_factor = 1.0
            self.update_image_scale()
            self.fit_to_window()

    def fit_to_window(self):
        # Ya no se usa: la imagen nunca se ajusta automáticamente
        pass

    def mouseDoubleClickEvent(self, event):
        # Centrar imagen al hacer doble clic
        self.fit_to_window()

    def wheelEvent(self, event):
        """Maneja el zoom con la rueda del mouse de forma amigable y controlada, siempre desde la imagen original para evitar borrosidad."""
        if self.scroll_area:
            self.scroll_area.setWidgetResizable(False)

        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        angle = event.angleDelta().y()
        if angle > 0:
            new_scale = self.scale_factor * zoom_in_factor
        elif angle < 0:
            new_scale = self.scale_factor * zoom_out_factor
        else:
            return

        # Clamp a los límites definidos
        new_scale = max(self._min_scale, min(self._max_scale, new_scale))
        if abs(new_scale - self.scale_factor) > 1e-4:
            self.scale_factor = new_scale
            self.update_image_scale()

    def update_image_scale(self):
        """Aplica el nuevo factor de escala a la imagen, siempre desde el original para evitar borrosidad. Permite mover la imagen libremente bajo el marco."""
        if self._original_pixmap is None or self._original_pixmap.isNull():
            return
        new_size = self._original_pixmap.size() * self.scale_factor
        scaled = self._original_pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled)
        self.resize(scaled.size())
        # No recentrar ni ajustar scrollbars

    def mousePressEvent(self, event):
        """Inicia el paneo (mover la imagen con el mouse)."""
        if event.button() == Qt.LeftButton:
            self.panning = True
            self.last_mouse_pos = event.pos()
            self.start_pos = self.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        """Realiza el paneo moviendo la imagen con el mouse dentro del canvas grande."""
        if self.panning and self.last_mouse_pos:
            delta = event.pos() - self.last_mouse_pos
            new_pos = self.start_pos + delta
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        """Termina el paneo."""
        if event.button() == Qt.LeftButton:
            self.panning = False
            self.last_mouse_pos = None
            self.setCursor(Qt.ArrowCursor)
        

class DialogoFormularios(QDialog):
    def resizeEvent(self, event):
        # Este evento es necesario para reposicionar los widgets superpuestos
        super().resizeEvent(event)
        if hasattr(self, 'mapa_view'):
            parent_width = self.mapa_view.parentWidget().width()
            parent_height = self.mapa_view.parentWidget().height()
            margin_y = 15
            spacing = 10

            # Centrar el combobox de símbolos y el botón de la cámara
            combo_size = self.combo_simbolo.sizeHint()
            camera_size = self.btn_guardar_captura.size()

            total_width = combo_size.width() + spacing + camera_size.width()
            start_x = (parent_width - total_width) // 2

            # Alineación vertical
            combo_height = self.combo_simbolo.sizeHint().height()
            camera_height = self.btn_guardar_captura.height()
            camera_y_offset = (combo_height - camera_height) // 2

            # Posiciones X
            combo_x = start_x
            camera_x = combo_x + combo_size.width() + spacing

            # Mover widgets
            self.combo_simbolo.move(combo_x, margin_y)
            self.btn_guardar_captura.move(camera_x, margin_y + camera_y_offset)

            # Mover botón de "Ver todos" a la esquina inferior izquierda
            reset_size = self.btn_reset_mapa.size()
            reset_x = 15
            reset_y = parent_height - reset_size.height() - 15
            self.btn_reset_mapa.move(reset_x, reset_y)


    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Generar Formularios")
        self.setFixedWidth(1350)
        self.setFixedHeight(800)
        self.df_coords = None
        self.excel_path = None
        self.output_dir = None
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #333;
                background: transparent;
                border: none;
            }
            QCheckBox {
                color: #333;
                font-size: 12px;
            }
            QCheckBox[text="Todo"] {
                font-weight: bold;
                color: #3498db;
            }
            QTableWidget {
                background: #ffffff;
                color: #333;
                font-size: 11px;
                border: 1px solid #ccc;
                border-radius: 5px;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background: #e9e9e9;
                color: #333;
                font-size: 11px;
                border: 1px solid #ccc;
                padding: 6px;
                font-weight: bold;
            }
            QTableWidget QLineEdit {
                background-color: #fff;
                color: #333;
                border: 1px solid #3498db;
            }
        """)

        # --- Layout principal horizontal ---
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)

        # --- Columna izquierda ---
        left_widget = QWidget()
        left_widget.setMaximumWidth(520) # Limita el ancho máximo de la columna izquierda
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)

        # Botones Excel arriba
        fila_excel = QHBoxLayout()
        self.btn_excel = QPushButton(" IMPORTAR DATA")
        self.btn_excel.setStyleSheet("background: #2ecc71; color: white; border: none; border-radius: 5px; font-size: 11px; font-weight: bold; padding: 8px;")
        self.btn_excel.hover = "background: #27ae60;"

        icon_path_excel = resource_path(os.path.join("Assets", "Image", "upload_excel.png"))
        if os.path.exists(icon_path_excel):
            self.btn_excel.setIcon(QIcon(icon_path_excel))
            self.btn_excel.setIconSize(QSize(22, 22))

        self.btn_plantilla = QPushButton(" DESCARGAR PLANTILLA")
        self.btn_plantilla.setStyleSheet("background: #3498db; color: white; border: none; border-radius: 5px; font-size: 11px; font-weight: bold; padding: 8px;")
        self.btn_plantilla.hover = "background: #2980b9;" # Este atributo no tiene efecto, es solo un comentario.

        icon_path_download = resource_path(os.path.join("Assets", "Image", "download_excel.png"))
        if os.path.exists(icon_path_download):
            self.btn_plantilla.setIcon(QIcon(icon_path_download))
            self.btn_plantilla.setIconSize(QSize(22, 22))

        fila_excel.addWidget(self.btn_excel)
        fila_excel.addWidget(self.btn_plantilla)
        left_layout.addLayout(fila_excel)
        self.lbl_estado = QLabel("")
        self.lbl_estado.setStyleSheet("font-size: 11px;")
        left_layout.addWidget(self.lbl_estado)

        # Checkboxes de formularios
        self.formularios = ["Formulario 001", "Formulario 002", "Formulario 003", "Formulario 004", "Formulario 005"]
        self.checks = []
        grid_checks = QGridLayout()
        grid_checks.setColumnStretch(0, 1) # Asegura que las columnas tengan el mismo ancho
        grid_checks.setColumnStretch(1, 1) # para un alineamiento visual correcto.
        
        for i, nombre in enumerate(self.formularios):
            chk = QCheckBox(nombre)
            chk.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
            self.checks.append(chk)

            fila = i % 3
            columna = i // 3
            grid_checks.addWidget(chk, fila, columna, alignment=Qt.AlignCenter)

        self.chk_todo = QCheckBox("Todo")
        self.chk_todo.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        grid_checks.addWidget(self.chk_todo, 2, 1, alignment=Qt.AlignCenter)
        left_layout.addLayout(grid_checks)
        left_layout.addSpacing(10) # Añade un espacio debajo de los checkboxes

        # Layout para el encabezado de la tabla de puntos (título y comboboxes)
        header_puntos_layout = QHBoxLayout()
        lbl_puntos_geodesicos = QLabel("Puntos Geodésicos")
        lbl_puntos_geodesicos.setStyleSheet("font-size: 13px; color: #2c3e50; font-weight: bold;")
        header_puntos_layout.addWidget(lbl_puntos_geodesicos)
        header_puntos_layout.addStretch()

        # ComboBox para Zona
        lbl_zona = QLabel("Zona:")
        lbl_zona.setStyleSheet("font-size: 12px;")
        self.combo_zona = QComboBox()
        self.combo_zona.addItems(["17 S", "18 S", "19 S"])
        self.combo_zona.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.combo_zona.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.combo_zona.setStyleSheet("""
            QComboBox {
                background: #fff;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 4px 18px 4px 10px;
                color: #2c3e50;
                font-size: 12px;
                min-width: 70px;
                box-shadow: 0 2px 8px rgba(52,152,219,0.08);
            }
            QComboBox:focus {
                border: 2px solid #2980b9;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 22px;
            }
            QComboBox::down-arrow {
                image: url(:/qt-project.org/styles/commonstyle/images/down-arrow.png);
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                background: #f0f0f0;
                color: #2c3e50;
                border-radius: 8px;
                selection-background-color: #3498db;
                selection-color: #fff;
            }
        """)
        header_puntos_layout.addWidget(lbl_zona)
        header_puntos_layout.addWidget(self.combo_zona)

        # ComboBox para Orden
        lbl_orden = QLabel("Orden:")
        lbl_orden.setStyleSheet("margin-left: 10px; font-size: 12px;")
        self.combo_orden = QComboBox()
        self.combo_orden.addItems(["A", "B", "C"])
        self.combo_orden.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.combo_orden.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.combo_orden.setStyleSheet("""
            QComboBox {
                background: #fff;
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 4px 18px 4px 10px;
                color: #2c3e50;
                font-size: 12px;
                min-width: 50px;
                box-shadow: 0 2px 8px rgba(52,152,219,0.08);
            }
            QComboBox:focus {
                border: 2px solid #2980b9;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 22px;
            }
            QComboBox::down-arrow {
                image: url(:/qt-project.org/styles/commonstyle/images/down-arrow.png);
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                background: #f0f0f0;
                color: #2c3e50;
                border-radius: 8px;
                selection-background-color: #3498db;
                selection-color: #fff;
            }
        """)
        header_puntos_layout.addWidget(lbl_orden)
        header_puntos_layout.addWidget(self.combo_orden)

        left_layout.addLayout(header_puntos_layout)

        # Tabla de puntos
        self.tabla_coords = QTableWidget()
        self.tabla_coords.setColumnCount(10)
        self.tabla_coords.setHorizontalHeaderLabels(["ID", "PUNTO", "ESTE", "NORTE", "LATITUD", "LONGITUD", "ALTURA ELIPSOIDAL", "FECHA", "HORA INICIO", "HORA FINAL"])
        self.tabla_coords.setMinimumHeight(200)
        left_layout.addWidget(self.tabla_coords)

        # Botón cargar imágenes con icono
        self.btn_cargar_imagenes = QPushButton(" CARGAR IMÁGENES")
        self.btn_cargar_imagenes.setStyleSheet("background: #9b59b6; color: white; border: none; border-radius: 5px; font-size: 11px; font-weight: bold; padding: 8px;")
        icon_path_image = resource_path(os.path.join("Assets", "Image", "image.png"))
        if os.path.exists(icon_path_image):
            self.btn_cargar_imagenes.setIcon(QIcon(icon_path_image))
            self.btn_cargar_imagenes.setIconSize(QSize(22, 22))
        self.btn_cargar_imagenes.clicked.connect(self.cargar_carpeta_imagenes)

        # Botón carpeta de imagen
        self.btn_carpeta_imagen = QPushButton("CREAR CARPETA IMG")
        self.btn_carpeta_imagen.setStyleSheet("background: #2980b9; color: white; font-size: 11px; font-weight: bold; border-radius: 5px; padding: 8px 24px;")
        icon_path_crear_carpeta = resource_path(os.path.join("Assets", "Image", "crear_carpeta.png"))
        if os.path.exists(icon_path_crear_carpeta):
            self.btn_carpeta_imagen.setIcon(QIcon(icon_path_crear_carpeta))
            self.btn_carpeta_imagen.setIconSize(QSize(22, 22))
        self.btn_carpeta_imagen.clicked.connect(self.crear_carpeta_imagenes)

        # Layout horizontal para ambos botones (uno al costado del otro)
        fila_botones_imagen = QHBoxLayout()
        fila_botones_imagen.addWidget(self.btn_cargar_imagenes)
        fila_botones_imagen.addWidget(self.btn_carpeta_imagen)
        left_layout.addLayout(fila_botones_imagen)

        if os.path.exists(icon_path_image):
            self.btn_cargar_imagenes.setIcon(QIcon(icon_path_image))
            self.btn_cargar_imagenes.setIconSize(QSize(22, 22))
        self.btn_cargar_imagenes.clicked.connect(self.cargar_carpeta_imagenes)
        # left_layout.addWidget(self.btn_cargar_imagenes)

        # Tabla de imágenes
        self.tabla_imagenes = QTableWidget()
        self.tabla_imagenes.setColumnCount(6)
        self.tabla_imagenes.setHorizontalHeaderLabels(["ID", "PUNTO", "UBICACION PG","POSICIONAMIENTO GPS-GNSS", "DISCO DE BRONCE", "ALTURA DE ANTENA"])
        self.tabla_imagenes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        left_layout.addWidget(self.tabla_imagenes)
        left_layout.addStretch()

        # Fila de botones abajo
        fila_botones = QHBoxLayout()
        self.btn_carpeta = QPushButton(" ELEGIR CARPETA")
        self.btn_carpeta.setStyleSheet("background: #e67e22; color: white; border: none; border-radius: 5px; font-size: 11px; font-weight: bold; padding: 8px;") # Icono de guardar
        icon_path_folder = resource_path(os.path.join("Assets", "Image", "guardar.png"))
        if os.path.exists(icon_path_folder):
            self.btn_carpeta.setIcon(QIcon(icon_path_folder))
            self.btn_carpeta.setIconSize(QSize(22, 22))
        self.btn_carpeta.clicked.connect(self.elegir_carpeta)

        self.btn_generar = QPushButton("GENERAR FORMULARIO")
        self.btn_generar.setStyleSheet("background: #16a085; color: white; border: none; border-radius: 5px; font-size: 11px; font-weight: bold; padding: 10px;")
        self.btn_generar.clicked.connect(self.generar)
        fila_botones.addWidget(self.btn_carpeta)
        fila_botones.addWidget(self.btn_generar)
        left_layout.addLayout(fila_botones)

        # --- Columna derecha ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)

        # Mapa satelital
        self.mapa_view = QWebEngineView()
        self.mapa_view.setMinimumHeight(600)
        right_layout.addWidget(self.mapa_view)

        # Botón para guardar captura del mapa, superpuesto
        self.btn_guardar_captura = QPushButton("", right_widget)
        self.btn_guardar_captura.setFixedSize(40, 40)
        self.btn_guardar_captura.setToolTip("Guardar captura del mapa")
        self.btn_guardar_captura.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 20px; /* La mitad del tamaño para hacerlo circular */
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 50);
            }
        """)
        icon_path_camera = resource_path(os.path.join("Assets", "Image", "camara.png"))
        if os.path.exists(icon_path_camera):
            self.btn_guardar_captura.setIcon(QIcon(icon_path_camera))
            self.btn_guardar_captura.setIconSize(QSize(30, 30))
        else:
            self.btn_guardar_captura.setText("📷") # Alternativa si no se encuentra el icono
        self.btn_guardar_captura.clicked.connect(self.guardar_captura)

        # ComboBox para seleccionar el símbolo del marcador, superpuesto
        self.combo_simbolo = QComboBox(right_widget)
        # Símbolos geométricos para los marcadores
        self.combo_simbolo.addItems(['Triángulo', 'Círculo', 'Cuadrado', 'Cruz', 'Estrella', 'Pin'])
        self.combo_simbolo.setToolTip("Seleccionar símbolo del marcador")
        self.combo_simbolo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid #ccc;
                border-radius: 18px; /* Ajustado para un borde perfectamente redondeado */
                padding: 8px 18px;
                color: #333;
                font-size: 12px;
                font-weight: bold;
                min-width: 140px;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: url(:/qt-project.org/styles/commonstyle/images/down-arrow.png);
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                background: #fff;
                border: 1px solid #ccc;
                border-radius: 10px;
                selection-background-color: #3498db;
                selection-color: #fff;
            }
        """)
        self.combo_simbolo.currentTextChanged.connect(lambda: self.mostrar_mapa())

        # Botón para ver todos los puntos (icono de ojo)
        self.btn_reset_mapa = QPushButton("", right_widget)
        self.btn_reset_mapa.setFixedSize(40, 40)
        self.btn_reset_mapa.setToolTip("MOSTRAR PUNTOS")
        self.btn_reset_mapa.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #ccc;
                border-radius: 20px; /* La mitad del tamaño para un círculo perfecto */
            }
            QPushButton:hover {
                background-color: #fff;
                border-color: #3498db;
            }
        """)
        icon_path_eye = resource_path(os.path.join("Assets", "Image", "eye.png"))
        if os.path.exists(icon_path_eye):
            self.btn_reset_mapa.setIcon(QIcon(icon_path_eye))
            # El icono debe ser más pequeño que el botón para que se vea el borde
            self.btn_reset_mapa.setIconSize(QSize(24, 24))
        else:
            self.btn_reset_mapa.setText("👁️") # Fallback emoji
        self.btn_reset_mapa.clicked.connect(lambda: self.mostrar_mapa())

        # Hacemos los widgets visibles
        self.btn_guardar_captura.show()
        self.combo_simbolo.show()
        self.btn_reset_mapa.show()
        # Usamos .raise_() para asegurar que el control se dibuje encima del mapa.
        self.btn_guardar_captura.raise_()
        self.combo_simbolo.raise_()
        self.btn_reset_mapa.raise_()

        # --- Añadir ambas columnas al layout principal ---
        main_layout.addWidget(left_widget, stretch=1)
        main_layout.addWidget(right_widget, stretch=2) # Reajustamos el stretch, el ancho ahora se controla con setMaximumWidth

        # --- Conexiones adicionales ---
        self.btn_excel.clicked.connect(self.cargar_excel)
        self.btn_plantilla.clicked.connect(self.descargar_plantilla)
        self.tabla_coords.itemSelectionChanged.connect(self.mostrar_punto_seleccionado)

        # ----- MOSTRARA MAPA
        self.mostrar_mapa()


        # --- Checkbox "Todo" ---
        def marcar_todos(state):
            for chk in self.checks:
                chk.setChecked(state == Qt.Checked)
        self.chk_todo.stateChanged.connect(marcar_todos)

        def actualizar_todo():
            if all(chk.isChecked() for chk in self.checks):
                self.chk_todo.setChecked(True)
            else:
                self.chk_todo.setChecked(False)
        for chk in self.checks:
            chk.stateChanged.connect(actualizar_todo)
        self.chk_todo.setChecked(False)
    
    def _create_image_icon_widget(self, image_path):
        """Crea un widget con un botón de icono para la celda de la tabla. Si la imagen existe, la muestra como miniatura."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)

        button = QPushButton()
        if image_path and os.path.exists(image_path):
            button.setIcon(QIcon(image_path))
        else:
            icon_path = resource_path(os.path.join("Assets", "Image", "imagen.png"))
            if os.path.exists(icon_path):
                button.setIcon(QIcon(icon_path))
            else:
                button.setText("🖼️") # Emoji de fallback

        button.setFixedSize(32, 32)
        button.setStyleSheet("QPushButton { border: none; background: transparent; }")
        button.setCursor(Qt.PointingHandCursor)
        button.setProperty("image_path", image_path) # Guardamos la ruta en el botón
        button.clicked.connect(self.show_image_preview)

        layout.addWidget(button)
        widget.setLayout(layout)
        return widget

    def show_image_preview(self):
        sender_button = self.sender()
        image_path_actual = sender_button.property("image_path")
        tipo_imagen = None
        # Detecta el tipo de imagen por la columna
        for fila in range(self.tabla_imagenes.rowCount()):
            for col, nombre in zip([2,3,4,5], ["UBICACION PG", "POSICIONAMIENTO GPS-GNSS", "DISCO DE BRONCE", "ALTURA DE ANTENA"]):
                widget = self.tabla_imagenes.cellWidget(fila, col)
                if widget:
                    btn = widget.findChild(QPushButton)
                    if btn is sender_button:
                        tipo_imagen = nombre
                        break
            if tipo_imagen:
                break
        if image_path_actual and os.path.exists(image_path_actual):
            dialog = ImageViewerDialog(image_path_actual, sender_button, parent=self, tipo_imagen=tipo_imagen)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "La ruta de la imagen no es válida o el archivo no existe.")



    def cargar_excel(self):
        # --- NUEVO: Pedir la zona primero ---
        zonas_disponibles = ["17 S", "18 S", "19 S"]
        zona_seleccionada, ok = QInputDialog.getItem(
            self,
            "Seleccionar Zona UTM",
            "Antes de continuar, por favor selecciona la zona UTM a la que pertenecen tus datos:",
            zonas_disponibles,
            0,  # Índice inicial
            False # No editable
        )

        if not ok or not zona_seleccionada:
            self.lbl_estado.setText("Operación cancelada. Se requiere una zona.")
            self.lbl_estado.setStyleSheet("color: #e67e22; background: transparent; font-size: 11px;")
            return

        # Actualizar el ComboBox de la interfaz para que refleje la selección
        self.combo_zona.setCurrentText(zona_seleccionada)

        # --- El resto de la función continúa como antes ---
        path, _ = QFileDialog.getOpenFileName(self, "Selecciona el archivo Excel", "", "Archivos Excel (*.xlsx)")
        if not path:
            self.lbl_estado.setText("")
            return

        self.excel_path = path
        try:
            # Mapeo de los nombres de columna del Excel a los nombres estándar de la app
            column_mapping = {
                'COD_PUNTO _GEODESICO': 'PUNTO',
                'ESTE_(E)_WGS-84': 'ESTE',
                'NORTE_(N)_WGS-84': 'NORTE',
                'LATITUD_(S)_WGS-84': 'LATITUD',
                'LONGITUD_(O)_WGS-84': 'LONGITUD',
                'ALTURA_ELIPSOIDAL_(M)': 'ALTURA ELIPSOIDAL',
                'FECHA_POSICIONAMIENTO': 'FECHA',
                'HORA_INICIO': 'HORA INICIO',
                'HORA_TERMINO': 'HORA FINAL',
            }

            # --- Lógica para leer la tabla con campos en vertical ---
            df_raw = pd.read_excel(path, sheet_name=2, header=None)
            df_transposed = df_raw.T
            df = df_transposed[1:]
            df.columns = df_transposed.iloc[0]

            rename_map = {}
            for col in df.columns:
                if pd.isna(col):
                    continue
                normalized_col = ' '.join(str(col).strip().upper().split())
                for key, value in column_mapping.items():
                    normalized_key = ' '.join(key.strip().upper().split())
                    if normalized_key == normalized_col:
                        rename_map[col] = value
                        break
            df.rename(columns=rename_map, inplace=True)
            
            if 'PUNTO' in df.columns:
                df.dropna(subset=['PUNTO'], inplace=True)
                df = df[df['PUNTO'].astype(str).str.strip() != '']
            df = df.reset_index(drop=True)

            # print("¡Lectura de Excel exitosa!")
            # print(f"Columnas encontradas y mapeadas: {list(df.columns)}")
            # print(f"Número de puntos encontrados: {len(df)}")

            required_cols = {'PUNTO', 'ESTE', 'NORTE', 'LATITUD', 'LONGITUD', 'ALTURA ELIPSOIDAL', 'FECHA', 'HORA INICIO', 'HORA FINAL'}
            if not required_cols.issubset(df.columns):
                missing = required_cols - set(df.columns)
                raise ValueError(f"Columnas requeridas no encontradas: {', '.join(missing)}")

            self.df_coords = df

            # --- Poblar la primera tabla (tabla_coords) ---
            self.tabla_coords.setRowCount(len(df))
            for i, row in df.iterrows():
                # Columna 0: ID
                self.tabla_coords.setItem(i, 0, QTableWidgetItem(str(i + 1)))

                # Columna 1: PUNTO
                punto_str = str(row.get('PUNTO', ''))
                try:
                    punto_str = str(int(float(punto_str)))
                except (ValueError, TypeError):
                    pass
                self.tabla_coords.setItem(i, 1, QTableWidgetItem(punto_str))

                # Obtener coordenadas y otros datos
                este = row.get('ESTE')
                norte = row.get('NORTE')
                lat = row.get('LATITUD')
                lon = row.get('LONGITUD')
                self.zona = self.combo_zona.currentText().replace(" S", "") # Se mantiene por si es necesario para el cálculo
                print ("zona: ", self.zona)

                # Calcular Lat/Lon si no existen
                if pd.isnull(lat) or pd.isnull(lon):
                    print ("esntro?")
                    if pd.notnull(este) and pd.notnull(norte):
                        try:
                            lat, lon = este_norte_a_latlon(este, norte, zona=int(self.zona))
                            print ("cooordendas: ", lat, lon)
                        except:
                            lat, lon = "", ""
                    else:
                        lat, lon = "", ""
                print ("no esntro")
                # Columna 2: ESTE
                self.tabla_coords.setItem(i, 2, QTableWidgetItem(f"{este:.3f}" if pd.notnull(este) and isinstance(este, (float, int)) else str(este or '')))
                
                # Columna 3: NORTE
                self.tabla_coords.setItem(i, 3, QTableWidgetItem(f"{norte:.3f}" if pd.notnull(norte) and isinstance(norte, (float, int)) else str(norte or '')))
                
                # Columna 4: LATITUD
                self.tabla_coords.setItem(i, 4, QTableWidgetItem(f"{lat:.6f}" if pd.notnull(lat) and isinstance(lat, (float, int)) else str(lat or '')))
                
                # Columna 5: LONGITUD
                self.tabla_coords.setItem(i, 5, QTableWidgetItem(f"{lon:.6f}" if pd.notnull(lon) and isinstance(lon, (float, int)) else str(lon or '')))

                # Columna 6: ALTURA ELIPSOIDAL
                altura = row.get('ALTURA ELIPSOIDAL', '')
                self.tabla_coords.setItem(i, 6, QTableWidgetItem(f"{altura:.3f}" if pd.notnull(altura) and isinstance(altura, (float, int)) else str(altura or '')))

                # Columna 7: FECHA
                fecha = row.get('FECHA', '')
                fecha_str = fecha.strftime('%Y-%m-%d') if isinstance(fecha, (datetime.datetime, pd.Timestamp)) else str(fecha or '')
                self.tabla_coords.setItem(i, 7, QTableWidgetItem(fecha_str))

                # Columna 8: HORA INICIO
                hora_inicio = row.get('HORA INICIO', '')
                hora_inicio_str = hora_inicio.strftime('%H:%M:%S') if isinstance(hora_inicio, (datetime.time, pd.Timestamp)) else str(hora_inicio or '')
                self.tabla_coords.setItem(i, 8, QTableWidgetItem(hora_inicio_str))

                # Columna 9: HORA FINAL
                hora_final = row.get('HORA FINAL', '')
                hora_final_str = hora_final.strftime('%H:%M:%S') if isinstance(hora_final, (datetime.time, pd.Timestamp)) else str(hora_final or '')
                self.tabla_coords.setItem(i, 9, QTableWidgetItem(hora_final_str))

            # --- Poblar la segunda tabla (tabla_imagenes) ---
            self.tabla_imagenes.setRowCount(len(df))
            for i, row in df.iterrows():
                self.tabla_imagenes.setItem(i, 0, QTableWidgetItem(str(i+1)))

                punto_str = str(row.get('PUNTO', ''))
                try:
                    punto_str = str(int(float(punto_str)))
                except (ValueError, TypeError):
                    pass
                self.tabla_imagenes.setItem(i, 1, QTableWidgetItem(punto_str))
            self.mostrar_mapa()
            self.lbl_estado.setStyleSheet("color: #4caf50; background: transparent; font-size: 11px;")
            self.lbl_estado.setText("Data cargada con éxito")

        except Exception as e:
            self.lbl_estado.setStyleSheet("color: #e53935; background: transparent; font-size: 13px;")
            self.lbl_estado.setText(f"Error al cargar: {e}")
            QMessageBox.critical(self, "Error al cargar Excel", str(e))
    
    
    def cargar_carpeta_imagenes(self):
        """
        Abre un diálogo para seleccionar una carpeta. Busca subcarpetas con el nombre
        de cada punto y carga las rutas de imágenes específicas en la tabla de imágenes.
        Esta versión es más robusta y maneja variaciones en mayúsculas/minúsculas.
        """
        if self.tabla_imagenes.rowCount() == 0:
            QMessageBox.warning(self, "Sin Puntos", "Primero debe cargar los datos de los puntos desde el archivo Excel.")
            return
        carpeta_principal = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta Principal de Imágenes", "")
        if not carpeta_principal:
            return

        # Mapeo de nombres de imagen base a su índice de columna en tabla_imagenes
        nombres_imagenes = {
            "UBICACION PG": 2,
            "POSICIONAMIENTO GPS-GNSS": 3,
            "DISCO DE BRONCE": 4,
            "ALTURA DE ANTENA": 5
        }
        
        try:
            # 1. Obtener una lista de todos los subdirectorios reales
            subdirs_reales = [d for d in os.listdir(carpeta_principal) if os.path.isdir(os.path.join(carpeta_principal, d))]
            
            puntos_con_imagenes = 0
            
            # 2. Iterar sobre las filas de la tabla de imágenes
            for fila in range(self.tabla_imagenes.rowCount()):
                item_punto = self.tabla_imagenes.item(fila, 1)
                if not item_punto:
                    continue
                
                nombre_punto_tabla = item_punto.text().strip()
                
                # 3. Encontrar la subcarpeta correspondiente (buscando si el nombre del punto está DENTRO del nombre de la carpeta)
                subcarpeta_encontrada = None
                for sub_dir in subdirs_reales:
                    if nombre_punto_tabla in sub_dir:
                        subcarpeta_encontrada = sub_dir
                        break
                
                if subcarpeta_encontrada:
                    subcarpeta_punto_path = os.path.join(carpeta_principal, subcarpeta_encontrada)
                    
                    # 4. Listar los archivos en la subcarpeta (mapeando nombre de archivo sin extensión y en minúsculas al nombre real)
                    files_in_subdir = {os.path.splitext(f)[0].lower(): f for f in os.listdir(subcarpeta_punto_path)}
                    se_encontro_alguna_imagen = False
                    
                    # 5. Buscar cada tipo de imagen requerida
                    for nombre_base, col_idx in nombres_imagenes.items():
                        nombre_base_lower = nombre_base.lower()
                        
                        # Buscar una coincidencia exacta del nombre base (ignorando extensión y mayúsculas)
                        if nombre_base_lower in files_in_subdir:
                            nombre_archivo_real = files_in_subdir[nombre_base_lower]
                            ruta_posible = os.path.join(subcarpeta_punto_path, nombre_archivo_real)
                            icon_widget = self._create_image_icon_widget(ruta_posible)
                            self.tabla_imagenes.setCellWidget(fila, col_idx, icon_widget)
                            se_encontro_alguna_imagen = True
                    
                    if se_encontro_alguna_imagen:
                        puntos_con_imagenes += 1
            
            if puntos_con_imagenes > 0:
                QMessageBox.information(self, "Éxito", f"Se han cargado imágenes para {puntos_con_imagenes} punto(s).")
            else:
                QMessageBox.warning(self, "Sin Coincidencias", "No se encontraron carpetas o imágenes que coincidan con los puntos de la tabla.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al procesar las imágenes: {e}")

    def crear_carpeta_imagenes(self):

        # Validar si hay elementos en la tabla de imágenes
        if self.tabla_imagenes.rowCount() == 0:
            QMessageBox.warning(self, "Sin puntos", "Primero debe importar la data para crear carpetas de imágenes.")
            return

        # Elegir carpeta destino
        carpeta_destino = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta donde guardar 'IMAGENES'", "")
        if not carpeta_destino:
            return

        # Carpeta principal
        carpeta_general = os.path.join(carpeta_destino, "IMAGENES")
        if not os.path.exists(carpeta_general):
            os.makedirs(carpeta_general)

        # Obtener nombres de los puntos geodésicos de la tabla de imágenes
        puntos = []
        for row in range(self.tabla_imagenes.rowCount()):
            punto = self.tabla_imagenes.item(row, 1)  # Columna "PUNTO"
            if punto:
                puntos.append(punto.text())

        # Crear subcarpetas
        for nombre in puntos:
            subcarpeta = os.path.join(carpeta_general, nombre)
            if not os.path.exists(subcarpeta):
                os.makedirs(subcarpeta)

        QMessageBox.information(self, "Carpetas creadas", "Las carpetas de imágenes han sido creadas correctamente.")

    def descargar_plantilla(self):
        plantilla_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Assets', 'Templates', 'FORMULARIOS_IQGeoSpatial.xlsx'))
        save_path, _ = QFileDialog.getSaveFileName(self, "Guardar plantilla Excel", "FORMULARIOS_IQGeoSpatial.xlsx", "Archivos Excel (*.xlsx)")
        if save_path:
            shutil.copyfile(plantilla_path, save_path)
            QMessageBox.information(self, "Descarga completada", "Plantilla descargada correctamente.")

    def elegir_carpeta(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de guardado", "")
        if carpeta:
            self.output_dir = carpeta
            QMessageBox.information(self, "Carpeta seleccionada", f"Carpeta: {carpeta}")

    def generar(self):
        seleccionados = [f for f, chk in zip(self.formularios, self.checks) if chk.isChecked()]
        if not self.excel_path:
            QMessageBox.warning(self, "Error", "Primero cargue el archivo Excel.")
            return
        if not self.output_dir:
            QMessageBox.warning(self, "Error", "Seleccione una carpeta de guardado.")
            return
        if not seleccionados:
            QMessageBox.warning(self, "Error", "Seleccione al menos un formulario.")
            return

        # --- Construir image_paths_dict a partir de la tabla_imagenes ---
        image_paths_dict = {}
        for fila in range(self.tabla_imagenes.rowCount()):
            item_punto = self.tabla_imagenes.item(fila, 1)
            if not item_punto:
                continue
            punto_nombre = item_punto.text().strip().replace(" ", "_")
            rutas = {}
            # Columnas: 2=UBICACION PG, 3=POSICIONAMIENTO GPS-GNSS, 4=DISCO DE BRONCE, 5=ALTURA DE ANTENA
            col_map = {
                "RUTA_UBICACION_PG": 2,
                "RUTA_POSICIONAMIENTO_GPS_GNSS": 3,
                "RUTA_DISCO_DE_BRONCE": 4,
                "RUTA_ALTURA_DE_ANTENA": 5
            }
            for key, col in col_map.items():
                widget = self.tabla_imagenes.cellWidget(fila, col)
                if widget:
                    btn = widget.findChild(QPushButton)
                    if btn:
                        ruta = btn.property("image_path")
                        if ruta and isinstance(ruta, str) and os.path.exists(ruta):
                            rutas[key] = ruta
            if rutas:
                image_paths_dict[punto_nombre] = rutas

        # --- Capturar valores seleccionados de Zona y Orden ---
        zona_seleccionada = self.combo_zona.currentText()
        orden_seleccionado = self.combo_orden.currentText()

        ok, resultado = self.controller.generar_formularios_word(
            self.excel_path, self.output_dir, seleccionados, image_paths_dict,
            zona_seleccionada, orden_seleccionado
        )
        if ok:
            QMessageBox.information(self, "Éxito", f"Formularios generados y comprimidos en:\n{resultado}")
        else:
            QMessageBox.critical(self, "Error", f"Ocurrió un error: {resultado}")

    def guardar_captura(self):
        image = self.mapa_view.grab()
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar captura", "UBICACION PG.png", "PNG (*.png)")
        if ruta:
            image.save(ruta)
    
    def mostrar_punto_seleccionado(self):
        selected_items = self.tabla_coords.selectedItems()
        if not selected_items or self.df_coords is None:
            return

        selected_row = self.tabla_coords.row(selected_items[0])

        if 0 <= selected_row < len(self.df_coords):
            punto_seleccionado_data = self.df_coords.iloc[selected_row]
            puntos_para_mapa = []
            try:
                zona_str = self.combo_zona.currentText().replace(" S", "")
                zona_int = int(zona_str)
                este = punto_seleccionado_data.get('ESTE')
                norte = punto_seleccionado_data.get('NORTE')
                lat, lon = este_norte_a_latlon(este, norte, zona_int)
                if lat is not None and lon is not None:
                    puntos_para_mapa.append({'lat': lat, 'lon': lon, 'row_data': punto_seleccionado_data})
                    # Llamar a mostrar_mapa con el punto específico
                    self.mostrar_mapa(puntos_especificos=puntos_para_mapa)
            except (ValueError, AttributeError, IndexError):
                pass # Ignorar si la conversión falla para una fila

    def mostrar_mapa(self, puntos_especificos=None):
        puntos_para_mapa = []
        centro_mapa = [-12, -77]
        zoom_inicial = 6

        # --- LÓGICA DE SELECCIÓN DE PUNTOS ---
        if puntos_especificos is not None:
            # Caso: se pasa un punto específico (o varios) para mostrar
            puntos_para_mapa = puntos_especificos
        else:
            # Al mostrar todos los puntos, se limpia la selección de la tabla
            # para evitar que se vuelva a disparar el evento de selección única.
            self.tabla_coords.blockSignals(True)
            self.tabla_coords.clearSelection()
            self.tabla_coords.blockSignals(False)
            # Caso: mostrar todos los puntos del DataFrame cargado
            if self.df_coords is not None and 'ESTE' in self.df_coords.columns and 'NORTE' in self.df_coords.columns:
                try:
                    zona_str = self.combo_zona.currentText().replace(" S", "")
                    zona_int = int(zona_str)
                    for _, row in self.df_coords.iterrows():
                        if pd.notnull(row['ESTE']) and pd.notnull(row['NORTE']):
                            lat, lon = este_norte_a_latlon(row['ESTE'], row['NORTE'], zona_int)
                            if lat is not None and lon is not None:
                                puntos_para_mapa.append({'lat': lat, 'lon': lon, 'row_data': row})
                except (ValueError, AttributeError):
                    pass

        # 2. Centrar el mapa si se encontraron puntos
        if puntos_para_mapa:
            primer_punto = puntos_para_mapa[0]
            centro_mapa = [primer_punto['lat'], primer_punto['lon']]
            # Si es un solo punto, hacer más zoom. Si son varios, menos zoom.
            zoom_inicial = 17 if len(puntos_para_mapa) == 1 else 14

        # 3. Crear el mapa base con el centro y zoom adecuados
        m = folium.Map(location=centro_mapa, zoom_start=zoom_inicial, max_zoom=22)

        # Inyectar CSS para hacer invisible el contenedor de la etiqueta por defecto.
        # Esto nos permite controlar completamente el estilo con el 'tooltip_style' de abajo,
        # eliminando el recuadro blanco con punta que aparece detrás.
        tooltip_container_style = """
        <style>
            /* Oculta el contenedor y la flecha por defecto del tooltip de forma forzada */
            .leaflet-tooltip {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
            }
            .leaflet-tooltip-tip { display: none !important; }
        </style>
        """
        m.get_root().header.add_child(folium.Element(tooltip_container_style))

        # Añadir un norte magnético personalizado
        north_arrow_html = """
            <div style="
                position: fixed; 
                top: 80px; /* Posición vertical original */
                right: 20px; 
                z-index: 1000;
                text-align: center;
                font-family: sans-serif;
                pointer-events: none;
            ">
                <div style="font-size: 24px; font-weight: bold; color: #FFFF00;">N</div>
                <svg width="40" height="50" viewbox="0 0 100 100" style="filter: drop-shadow(2px 2px 2px rgba(0,0,0,0.3));">
                    <path d="M 50 5 L 85 95 L 50 70 L 15 95 Z" style="fill:#000000; stroke:#FFFF00; stroke-width:8; stroke-linejoin:round;" />
                </svg>
            </div>
        """
        m.get_root().html.add_child(folium.Element(north_arrow_html))

        # 4. Añadir las capas de mapas
        folium.TileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='OpenTopoMap', name='Topografía', overlay=False, control=True).add_to(m)
        folium.TileLayer('OpenStreetMap', name='Estándar (OpenStreetMap)').add_to(m)
        folium.TileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri", name="Satélite (Esri)").add_to(m)
        folium.TileLayer("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google", name="Satélite (Google)").add_to(m)

        # 5. Añadir los marcadores al mapa
        for punto in puntos_para_mapa:
            lat, lon, row_data = punto['lat'], punto['lon'], punto['row_data']
            nombre = row_data.get('PUNTO', row_data.get('CODIGO', ''))
            simbolo_seleccionado = self.combo_simbolo.currentText()

            try:
                nombre_str = str(int(float(nombre)))
            except (ValueError, TypeError):
                nombre_str = str(nombre)

            # Crear el marcador según el símbolo seleccionado
            if simbolo_seleccionado == 'Círculo':
                marker = folium.CircleMarker(
                    location=[lat, lon],
                    radius=7,
                    color='#cc0000',
                    weight=2,
                    fill=True,
                    fill_color='#ff3333',
                    fill_opacity=0.8,
                    popup=nombre_str
                )
            elif simbolo_seleccionado == 'Triángulo':
                marker = folium.RegularPolygonMarker(
                    location=[lat, lon],
                    number_of_sides=3,
                    radius=10,
                    rotation=0,
                    color='#cc0000',
                    fill_color='#ff3333',
                    fill_opacity=0.8,
                    popup=nombre_str
                )
            elif simbolo_seleccionado == 'Cuadrado':
                marker = folium.RegularPolygonMarker(
                    location=[lat, lon],
                    number_of_sides=4,
                    radius=9,
                    rotation=45, # Para que parezca un diamante
                    color='#cc0000',
                    fill_color='#ff3333',
                    fill_opacity=0.8,
                    popup=nombre_str
                )
            elif simbolo_seleccionado == 'Cruz':
                marker = folium.Marker(
                    location=[lat, lon],
                    popup=nombre_str,
                    icon=folium.DivIcon(html=f"""<div style="font-size: 24px; font-weight: bold; color: #ff3333; position: relative; left: -12px; top: -12px; text-shadow: 1px 1px 2px #000;">+</div>""")
                )
            elif simbolo_seleccionado == 'Estrella':
                marker = folium.Marker(
                    location=[lat, lon],
                    popup=nombre_str,
                    icon=folium.DivIcon(html=f"""<div style="font-size: 28px; color: #ff3333; position: relative; left: -14px; top: -14px; text-shadow: 1px 1px 2px #000;">★</div>""")
                )
            else: # Pin (o cualquier otro caso)
                marker = folium.Marker(
                    location=[lat, lon],
                    popup=nombre_str,
                    icon=folium.Icon(color='red', icon='info-sign')
                )
            # Estilo para el tooltip: caja amarilla, borde redondeado, texto negro.
            # Leaflet (la librería base de Folium) añade automáticamente una pequeña
            # flecha que apunta al marcador cuando el tooltip tiene un fondo visible.
            tooltip_style = """
                background-color: #ffff00; /* Amarillo brillante */
                border: 1px solid #555;
                border-radius: 10px; /* Borde más redondeado */
                color: black;
                font-size: 12px;
                font-weight: bold;
                padding: 5px 8px;
                box-shadow: 2px 2px 3px rgba(0,0,0,0.4); /* Sombra suave */
            """
            folium.Tooltip(
                text=f"<b>{nombre_str}</b>",
                permanent=True,
                direction='auto',
                style=tooltip_style
            ).add_to(marker)
            marker.add_to(m)

        # 6. Añadir control de capas y renderizar
        folium.LayerControl().add_to(m)
        temp_html = os.path.join(tempfile.gettempdir(), "mapa_temp.html")
        m.save(temp_html)
        self.mapa_view.load(QUrl.fromLocalFile(temp_html))
    

    def update_button_image(self, button, new_image_path):
        """Updates the button's icon with the new image."""
        if new_image_path and os.path.exists(new_image_path):
            button.setProperty("image_path", new_image_path)  # Update the image path
            icon = QIcon(new_image_path)  # Create a new icon
            button.setIcon(icon)  # Set the new icon
            button.setIconSize(QSize(32, 32))  # Ensure the icon size is correct





                    

class ExpedienteApp(QWidget):
    def closeEvent(self, event):
        # Solo cierra diálogos hijos abiertos (no ventanas principales)
        for widget in QApplication.topLevelWidgets():
            if widget is not self and widget.isVisible():
                # Cierra solo si es QDialog y su parent es self
                if isinstance(widget, QDialog) and widget.parent() is self:
                    widget.close()
        event.accept()
    def __init__(self):
        super().__init__()
        self.fechas_lectura = []
        self.db = CodigoDB()
        self.model = ExpedienteModel()
        self.controller = ExpedienteController(self.model, self, self.db)
        puntos_layout = QVBoxLayout()
        self.setWindowTitle("EXPEDIENTE DE CERTIFICACIÓN DE PUNTOS GEODÉSICOS")
        folder_icon_path = resource_path(os.path.join("Assets", "Image", "carpeta.png"))
        if os.path.exists(folder_icon_path):
            self.setWindowIcon(QIcon(folder_icon_path))
        self.setFixedSize(800, 700)
        self.setStyleSheet(
            """
            QWidget {
                background: #f0f0f0; /* Fondo color hueso */
                border-radius: 0px;
            }
            QLabel#Titulo {
                color: #2c3e50; /* Azul oscuro */
                font-size: 24px;
                font-weight: bold;
            }
            QLineEdit {
                background: #ffffff;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 12px;
                padding: 8px;
            }
            QCheckBox {
                color: #333;
                font-size: 12px;
            }
            QPushButton {
                background: #3498db;
                color: #fff;
                border: none;
                border-radius: 5px;
                font-size: 12px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton#Secundario {
                background: #e0e0e0;
                color: #333;
                border: 1px solid #ccc;
                font-size: 12px;
            }
            QPushButton#Secundario:hover {
                background: #d0d0d0;
                border-color: #3498db;
            }
            QLabel#Success { color: #27ae60; }
            QLabel#Error { color: #c0392b; }
            QLabel#Carpeta { color: #555; }
            QLabel#CampoAzul {
                color: #3498db;
                font-size: 12px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: #3498db;
                font-size: 16px;
                font-weight: bold;
            }
            .CampoPlomo, QLabel {
                color: #555;
                font-size: 12px;
            }
            QComboBox {
                background: #fff;
                border: 2px solid #3498db;
                color: #2c3e50;
                font-size: 13px;
                border-radius: 12px;
                padding: 6px 18px;
                font-weight: bold;
                outline: none;
            }
            QComboBox:focus {
                border: 2px solid #2980b9;
            }
            QComboBox QAbstractItemView {
                background: #fff;
                color: #2c3e50;
                border-radius: 12px;
                selection-background-color: #3498db;
                selection-color: #fff;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 22px;
            }
            QComboBox::down-arrow {
                image: url(:/qt-project.org/styles/commonstyle/images/down-arrow.png);
                width: 14px;
                height: 14px;
            }
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 10px;
                margin-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """
        )

        self.folder_path = os.path.expanduser("~\\Desktop")
       

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 20)

        # --- Top bar: imagen grande + título centrados ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(18)

        carpeta_img_path = resource_path(os.path.join("Assets", "Image", "caprtea_abierta.png"))
        self.carpeta_label = QLabel()
        if os.path.exists(carpeta_img_path):
            pixmap = QPixmap(carpeta_img_path).scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.carpeta_label.setPixmap(pixmap)
        self.carpeta_label.setFixedSize(120, 120)
        self.carpeta_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.carpeta_label)

        self.estructura_label = QLabel("ESTRUCTURA DE CARPETA IGN 2025")
        self.estructura_label.setObjectName("Titulo")
        self.estructura_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        font = self.estructura_label.font()
        font.setPointSize(18)
        font.setBold(True)
        self.estructura_label.setFont(font)
        header_layout.addWidget(self.estructura_label)

        # Centrar el header_widget en el main_layout
        main_layout.addWidget(header_widget, alignment=Qt.AlignHCenter)
        main_layout.addSpacing(10)

        # --- Proyecto ---
        proyecto_box = QVBoxLayout()
        lbl_proyecto = QLabel("Expediente")
        lbl_proyecto.setObjectName("CampoAzul")
        proyecto_box.addWidget(lbl_proyecto, alignment=Qt.AlignLeft)
        nombre_layout = QHBoxLayout()
        self.nombre_expediente = QLineEdit()
        self.nombre_expediente.setPlaceholderText("Nombre de Expediente")
        nombre_layout.addWidget(self.nombre_expediente)

        # Botón Guardar (solo icono)
        btn_save = QPushButton("")
        btn_save.setToolTip("Guardar nombre y seleccionar carpeta de destino")
        btn_save.setFixedSize(34, 34)
        icon_path_save = resource_path(os.path.join("Assets", "Image", "guardar.png"))
        if os.path.exists(icon_path_save):
            btn_save.setIcon(QIcon(icon_path_save))
            btn_save.setIconSize(QSize(28, 28))
        btn_save.setStyleSheet("QPushButton { border-radius: 6px; border: 1px solid #555; background: transparent;} QPushButton:hover { border-color: #2ecc71; }")

        # Botón Limpiar (solo icono)
        btn_limpiar = QPushButton("")
        btn_limpiar.setToolTip("Limpiar formulario")
        btn_limpiar.setFixedSize(34, 34)
        icon_path_limpiar = resource_path(os.path.join("Assets", "Image", "limpiar.png"))
        if os.path.exists(icon_path_limpiar):
            btn_limpiar.setIcon(QIcon(icon_path_limpiar))
            btn_limpiar.setIconSize(QSize(28, 28))
        btn_limpiar.setStyleSheet("QPushButton { border-radius: 6px; border: 1px solid #555; background: transparent;} QPushButton:hover { border-color: #e67e22; }")

        nombre_layout.addWidget(btn_save)
        nombre_layout.addWidget(btn_limpiar)
        proyecto_box.addLayout(nombre_layout)
        main_layout.addLayout(proyecto_box)
        main_layout.addSpacing(10)

        btn_save.clicked.connect(self.seleccionar_carpeta)
        btn_limpiar.clicked.connect(self.limpiar_expediente)

        # --- Puntos Geodésicos y Días de Lectura (Diseño igual a la imagen) ---
        seccion_layout = QHBoxLayout()

        # --- Grupo Puntos Geodésicos ---
        grupo_puntos = QGroupBox("Puntos Geodésicos")
        
        puntos_layout = QGridLayout()
        # El layout de tags se usará para mostrar los códigos generados
        self.tags_container = QGridLayout()
        main_layout.addLayout(self.tags_container)

        # Cod. Base
        lbl_cod_base = QLabel("Cod. Base")
        lbl_cod_base.setObjectName("CampoPlomo")
        self.cod_base = QComboBox()
        self.cod_base.setEditable(True)
        self.cod_base.addItems([str(1000707 + i) for i in range(10)])
        self.cod_base.setFixedWidth(180)
        self.cod_base.setFixedHeight(34)
        puntos_layout.addWidget(lbl_cod_base, 0, 0)
        puntos_layout.addWidget(self.cod_base, 1, 0)

        # Nº de Códigos
        lbl_num_codigos = QLabel("Nº de Códigos")
        lbl_num_codigos.setObjectName("CampoPlomo")
        self.num_codigos = QComboBox()
        self.num_codigos.setEditable(True)
        self.num_codigos.addItems([str(i) for i in range(1, 21)])
        self.num_codigos.setFixedWidth(180)
        self.num_codigos.setFixedHeight(34)
        puntos_layout.addWidget(lbl_num_codigos, 0, 1)
        puntos_layout.addWidget(self.num_codigos, 1, 1)

        # Incremento
        lbl_incremento = QLabel("Incremento")
        lbl_incremento.setObjectName("CampoPlomo")
        self.incremento = QComboBox()
        self.incremento.setEditable(True)
        self.incremento.addItems([str(i) for i in range(1, 6)])
        self.incremento.setFixedWidth(180)
        self.incremento.setFixedHeight(34)
        puntos_layout.addWidget(lbl_incremento, 2, 0)
        puntos_layout.addWidget(self.incremento, 3, 0)

        # Botón Generar Códigos (centrado en la columna 1, fila 3)
        btn_generar_codigos = QPushButton("Generar Códigos")
        btn_generar_codigos.setObjectName("Secundario")
        btn_generar_codigos.clicked.connect(self.controller.generar_codigos)
        puntos_layout.addWidget(btn_generar_codigos, 3, 1, alignment=Qt.AlignCenter)

        # Botón Ver Códigos (aparece después de generar)
        self.btn_ver_codigos = QPushButton("Ver Códigos Generados")
        self.btn_ver_codigos.setObjectName("Secundario")
        self.btn_ver_codigos.hide()
        self.btn_ver_codigos.clicked.connect(self.ventana_codigos)
        puntos_layout.addWidget(self.btn_ver_codigos, 4, 0, 1, 2, alignment=Qt.AlignCenter)

        # Mensaje de éxito
        self.lbl_codigos = QLabel("")
        self.lbl_codigos.setObjectName("Success")
        puntos_layout.addWidget(self.lbl_codigos, 5, 0, 1, 2, alignment=Qt.AlignCenter)

        # # --- SECCIÓN DE ENTRADA MANUAL COMENTADA ---
        # # Separador
        # linea_separadora = QFrame()
        # linea_separadora.setFrameShape(QFrame.HLine)
        # linea_separadora.setFrameShadow(QFrame.Sunken)
        # puntos_layout.addWidget(linea_separadora, 6, 0, 1, 2)

        # # Sección de agregado manual
        # lbl_manual = QLabel("O agregar manualmente:")
        # lbl_manual.setObjectName("CampoPlomo")
        # puntos_layout.addWidget(lbl_manual, 7, 0, 1, 2)

        # self.puntos_manuales_layout = QVBoxLayout()
        # self.puntos_manuales_layout.setSpacing(5)
        
        # scroll_content = QWidget()
        # scroll_content.setLayout(self.puntos_manuales_layout)
        
        # scroll_area = QScrollArea()
        # scroll_area.setWidgetResizable(True)
        # scroll_area.setWidget(scroll_content)
        # scroll_area.setMinimumHeight(80)
        # puntos_layout.addWidget(scroll_area, 8, 0, 1, 2)

        grupo_puntos.setLayout(puntos_layout)

        # --- Grupo Días de Lectura PG ---
        grupo_fechas = QGroupBox("Días de Lectura PG")
        
        fechas_layout = QVBoxLayout()
        fila3 = QHBoxLayout()
        lbl_num_dias = QLabel("Nº días")
        lbl_num_dias.setObjectName("CampoPlomo")
        self.num_dias = QComboBox()
        self.num_dias.setEditable(True)
        self.num_dias.addItems([str(i) for i in range(1, 11)])
        self.num_dias.setMinimumWidth(150)
        self.num_dias.currentIndexChanged.connect(self.actualizar_estado_botones_fechas)
        self.num_dias.editTextChanged.connect(self.actualizar_estado_botones_fechas) 


        fila3.addWidget(lbl_num_dias)
        fila3.addWidget(self.num_dias)

        # Botón Fechas (solo icono)
        self.btn_fechas = FechasButton(self, lambda: self.num_dias.currentText())
        self.btn_fechas.setText("")
        self.btn_fechas.setToolTip("Añadir fechas de lectura")
        self.btn_fechas.setFixedSize(34, 34)
        icon_path_calendar = resource_path(os.path.join("Assets", "Image", "calendario.png"))
        if os.path.exists(icon_path_calendar):
            self.btn_fechas.setIcon(QIcon(icon_path_calendar))
            self.btn_fechas.setIconSize(QSize(30, 30))
        self.btn_fechas.setStyleSheet("QPushButton { border-radius: 6px; border: 1px solid #555; background: transparent;} QPushButton:hover { border-color: #3498db; }")

        fila3.addWidget(self.btn_fechas)
        self.btn_fechas.clicked.connect(self.validar_fechas_pg)
        fechas_layout.addLayout(fila3)

        self.btn_ver_fechas = QPushButton("Ver días de lectura")
        self.btn_ver_fechas.setObjectName("Secundario")
        self.btn_ver_fechas.clicked.connect(self.ventana_fechas_lectura)
        fechas_layout.addWidget(self.btn_ver_fechas)

        # ...ahora sí llama a la función:
        self.actualizar_estado_botones_fechas()
        # Lista de códigos generados
        self.lista_codigos = QVBoxLayout()
        fechas_layout.addLayout(self.lista_codigos)
        grupo_fechas.setLayout(fechas_layout)

        # --- Añadir ambos grupos al layout horizontal ---
        seccion_layout.addWidget(grupo_puntos, stretch=1)
        seccion_layout.addWidget(grupo_fechas, stretch=1)
        main_layout.addLayout(seccion_layout)
        main_layout.addSpacing(10)

        # --- Checkboxes ---
        checks_layout = QHBoxLayout()
        self.chk_video = QCheckBox("Carpeta de Video")
        self.chk_verif = QCheckBox("Verificación de Coordenadas")
        checks_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        checks_layout.addWidget(self.chk_video)
        checks_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        checks_layout.addWidget(self.chk_verif)
        checks_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        main_layout.addLayout(checks_layout)
        main_layout.addSpacing(10)

        # --- Botón Crear Expediente ---
        btn_crear = QPushButton(" CREAR EXPEDIENTE")
        btn_crear.setObjectName("Secundario") # Le damos un estilo más sutil
        icon_path_crear = resource_path(os.path.join("Assets", "Image", "carpeta.png"))
        # 
        # ("[DEBUG] icon_path_crear:", icon_path_crear)
        # print("[DEBUG] Existe icon_path_crear:", os.path.exists(icon_path_crear))
        if os.path.exists(icon_path_crear):
            btn_crear.setIcon(QIcon(icon_path_crear))
            btn_crear.setIconSize(QSize(22, 22))
        btn_crear.clicked.connect(self.crear_estructura)
        main_layout.addWidget(btn_crear, alignment=Qt.AlignCenter)
        main_layout.addSpacing(10)

        # --- Barra de progreso y mensajes ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(100)
        main_layout.addWidget(self.progress_bar)
        self.lbl_resultado = QLabel("Expediente creado con éxito ...............")
        self.lbl_resultado.setObjectName("Success")
        main_layout.addWidget(self.lbl_resultado)
        main_layout.addSpacing(10)

        # Ocultar al inicio de barra
        self.progress_bar.setVisible(False)
        self.lbl_resultado.setVisible(False)

        # --- Carpeta destino ---
        self.lbl_carpeta = QLabel(f"Carpeta Destino: {self.folder_path}")
        self.lbl_carpeta.setObjectName("Carpeta")
        main_layout.addWidget(self.lbl_carpeta)

        self.lista_puntos = [] # Se usará para los tags de códigos generados
        # self.add_punto_geodesico_widget() # Comentado: ya no se añade widget manual por defecto

        self.setLayout(main_layout)
    
        #Agrega este método en tu clase principal (por ejemplo, MainWindow o similar):
    def mostrar_dialogo_licencia(self):
        dialog = LicenciaDialog(self)
        dialog.exec_()
    # ...existing code...

    def guardar_expediente(self):
        nombre = self.nombre_expediente.text().strip()
        if not nombre:
            mostrar_mensaje(self,"Advertencia", "Ingrese el nombre del expediente.", QMessageBox.Warning)
            return
        # Aquí puedes guardar el expediente en la base de datos o donde corresponda
        mostrar_mensaje(self,"Guardado", f"Expediente '{nombre}' guardado correctamente.", QMessageBox.Information)

    def limpiar_expediente(self):
        # Limpia nombre de expediente
        self.nombre_expediente.clear()
        # Limpia puntos geodésicos visuales y en memoria
        if hasattr(self, "lista_puntos"):
            self.lista_puntos = []
        self.actualizar_tags_grid()
        # Limpia códigos generados de la base de datos
        if self.db:
            for codigo, _ in self.db.obtener_codigos():
                self.db.eliminar_codigo(codigo)
        self.lbl_codigos.setText("")
        self.btn_ver_codigos.hide()
        # Limpia fechas de lectura
        if hasattr(self, "fechas_lectura"):
            self.fechas_lectura = []
        
        # Limpia mensajes y barra de progreso
        self.lbl_resultado.setText("")
        self.lbl_resultado.setVisible(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        self.num_dias.setCurrentIndex(0)  # Esto selecciona el primer valor ("1")
        self.actualizar_estado_botones_fechas()  # Opcional: para actualizar el estado de los botones

        self.num_dias.setCurrentIndex(0)      # Esto selecciona el primer valor ("1")
        self.num_codigos.setCurrentIndex(0)   # Esto selecciona el primer valor ("1")
        self.actualizar_estado_botones_fechas()

     # Ventanas de codigos generados
    def ventana_codigos(self):

        dialog = QDialog(self)
        dialog.setWindowTitle("Códigos Generados")
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        vbox = QVBoxLayout(content)

        codigos = self.db.obtener_codigos() if self.db else []
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Códigos Generados")
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        vbox = QVBoxLayout(content)
        content.setLayout(vbox)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        dialog.setLayout(layout)
        dialog.resize(400, 400)
        # Llama a la función para poblar la lista
        self.actualizar_lista_codigos(dialog)
        # dialog.exec_()

        content.setLayout(vbox)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        dialog.setLayout(layout)
        dialog.resize(400, 400)
        dialog.exec_()


    def actualizar_lista_codigos(self, dialog):
        # Busca el scroll area y su contenido
        scroll = dialog.findChild(QScrollArea)
        if not scroll:
            return
        content = scroll.widget()
        if not content:
            return
        # Limpia el layout
        layout = content.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        # Vuelve a agregar los códigos
        codigos = self.db.obtener_codigos() if self.db else []
        for codigo, _ in codigos:
            hbox = QHBoxLayout()
            lbl = QLabel(f"{codigo}")
            lbl.setObjectName("CampoPlomo")
            btn_x = QPushButton("X")
            btn_x.setFixedSize(28, 28)
            btn_x.setStyleSheet("color: red; font-weight: bold; background: #fff; border: 1px solid #3498db; border-radius: 6px;")
            btn_x.clicked.connect(lambda _, c=codigo: self.controller.eliminar_codigo_dialog(c, dialog))
            btn_p = QPushButton("P")
            btn_p.setFixedSize(28, 28)
            btn_p.setStyleSheet("color: #3498db; font-weight: bold; background: #fff; border: 1px solid #3498db; border-radius: 6px;")
            btn_p.clicked.connect(lambda _, c=codigo: self.controller.editar_codigo_dialog(c, dialog))
            hbox.addWidget(lbl)
            hbox.addWidget(btn_x)
            hbox.addWidget(btn_p)
            item_widget = QWidget()
            item_widget.setLayout(hbox)
            layout.addWidget(item_widget)


    def eliminar_codigo(self, codigo):
        # Elimina de la base de datos
        if self.db:
            self.db.eliminar_codigo(codigo)

    def ver_codigos(self):
        # Aquí puedes mostrar una ventana o mensaje con los códigos generados
        mostrar_mensaje(self,"Códigos Generados", "¡Códigos generados con éxito y almacenados en la base de datos!", QMessageBox.Information)

    def seleccionar_carpeta(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de guardado", self.folder_path)
        if carpeta:
            self.folder_path = carpeta
            self.lbl_carpeta.setText(f"Carpeta destino: {self.folder_path}")
    
    def actualizar_tags_grid(self):
        # Limpia el grid
        while self.tags_container.count():
            item = self.tags_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        # Vuelve a agregar los tags, 3 por fila
        if hasattr(self, "lista_puntos"):
            for idx, (nombre, tag_widget) in enumerate(self.lista_puntos):
                row = idx // 3   
                col = idx % 3    
                self.tags_container.addWidget(tag_widget, row, col)

    # --- MÉTODOS PARA WIDGETS MANUALES COMENTADOS ---
    # def add_punto_geodesico_widget(self):
    #     """Añade un nuevo widget para ingresar un punto geodésico."""
    #     widget = PuntoGeodesicoWidget(self.puntos_manuales_layout, self.remove_punto_geodesico_widget, self.add_punto_geodesico_widget)
    #     self.lista_puntos.append(widget)
    #     self.puntos_manuales_layout.addWidget(widget)
    #     self.actualizar_botones_puntos()

    # def remove_punto_geodesico_widget(self, widget):
    #     """Elimina un widget de punto geodésico."""
    #     if widget in self.lista_puntos:
    #         self.lista_puntos.remove(widget)
    #         widget.deleteLater()
    #         self.actualizar_botones_puntos()

    # def actualizar_botones_puntos(self):
    #     """Asegura que solo el último widget tenga el botón '+' y que no se pueda eliminar el único widget."""
    #     for i, widget in enumerate(self.lista_puntos):
    #         widget.btn_add.setVisible(i == len(self.lista_puntos) - 1)
    #         widget.btn_remove.setEnabled(len(self.lista_puntos) > 1)


    def crear_estructura(self):
        # Se registra un uso de la aplicación. Si no hay licencia,
        # esto incrementará el contador de usos de prueba.
        registrar_uso()

        expediente = self.nombre_expediente.text().strip().upper()
        if not expediente:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Ingrese el nombre del proyecto.")
            msg.exec_()
            return

        # Inicializa la lista de puntos vacía, ya que solo usaremos los generados
        puntos = []

        # 2. Agrega los códigos generados de la base de datos (si no están ya)
        codigos_generados = [codigo for codigo, _ in self.db.obtener_codigos()] if self.db else []
        if not codigos_generados:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Aún no se agregaron códigos de puntos geodésicos.\nPor favor, genera los códigos antes de crear el expediente.")
            msg.exec_()
            return
        
        for codigo in codigos_generados:
            if codigo not in puntos:
                puntos.append(codigo)

        # Mostrar barra de progreso inmediatamente
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.lbl_resultado.setText("")

        def finish_creation():
            fechas_pg = [f for f, _ in getattr(self, "fechas_lectura", [])]
            
            # Llama al método del controlador, que ahora se encarga de la lógica
            ok, mensaje = self.controller.crear_expediente_estructura(
                expediente=expediente,
                puntos=puntos,
                agregar_video=self.chk_video.isChecked(),
                agregar_verif=self.chk_verif.isChecked(),
                carpeta_base=self.folder_path,
                fechas_pg=fechas_pg
            )

            self.progress_bar.setValue(100)
            self.lbl_resultado.setObjectName("Success" if ok else "Error")
            self.lbl_resultado.setText(mensaje)

        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setVisible(True)
        self.lbl_resultado.setText("")
        self.lbl_resultado.setObjectName("Success")

        self.progress_bar.setVisible(True)
        self.lbl_resultado.setVisible(True)

        def update_progress(val=0):
            if val < 100:
                self.progress_bar.setValue(val)
                QTimer.singleShot(10, lambda: update_progress(val + 5))
            else:
                finish_creation()

        update_progress()
    
    #Meotodo de mostrar el calendario

    def mostrar_calendario(self):
        num_dias = int(self.num_dias.currentText())
        def agregar_y_repetir():
            dialog = QDialog(self)
            dialog.setWindowTitle("Seleccionar Fecha")
            layout = QVBoxLayout(dialog)
            calendar = QCalendarWidget() # Usará el estilo por defecto del sistema
            layout.addWidget(calendar)
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            layout.addWidget(buttons)

            def aceptar():
                selected_date = calendar.selectedDate()
                fecha = selected_date.toString("yyyy-MM-dd")
                self.controller.agregar_fecha_lectura(fecha)
                dialog.accept()
                # Si faltan fechas, vuelve a abrir el calendario
                if len(self.fechas_lectura) < num_dias:
                    agregar_y_repetir()
                else:
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Fechas agregadas")
                    msg.setIcon(QMessageBox.Information)
                    msg.setText(f"Se agregaron {num_dias} fechas.")
                    msg.exec_()

            buttons.accepted.connect(aceptar)
            buttons.rejected.connect(dialog.reject)
            dialog.exec_()

        # Solo si faltan fechas, inicia el proceso
        if len(self.fechas_lectura) < num_dias:
            agregar_y_repetir()
        else:
            #QMessageBox.information(self, "Límite alcanzado", f"Ya agregaste {num_dias} fechas.")
            msg = QMessageBox(self)
            msg.setWindowTitle("Límite alcanzado")
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"Ya agregaste {num_dias} fechas.")
            msg.exec_()

    # MOstrar ventana de echas

    def ventana_fechas_lectura(self):
        if not hasattr(self, "fechas_lectura") or not self.fechas_lectura:
            #QMessageBox.information(self, "Sin fechas", "No hay fechas cargadas.")
            msg = QMessageBox(self)
            msg.setWindowTitle("fechas_lectura")
            msg.setIcon(QMessageBox.Information)
            msg.setText("Sin fechas", "No hay fechas cargadas.")
            msg.exec_()
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Días de Lectura PG")
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        vbox = QVBoxLayout(content)
        content.setLayout(vbox)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        dialog.setLayout(layout)
        dialog.resize(400, 400)

        # Agrega las fechas guardadas
        for fecha, _ in self.fechas_lectura:
            hbox = QHBoxLayout()
            lbl = QLabel(f"Datos Estacion Base - {fecha}")
            btn_x = QPushButton("X")
            btn_x.setFixedSize(28, 28)
            btn_x.setStyleSheet("color: red; font-weight: bold; background: #fff; border: 1px solid #3498db; border-radius: 6px;")
            btn_x.clicked.connect(lambda _, f=fecha: self.eliminar_fecha_dialog(f, dialog))
            btn_p = QPushButton("P")
            btn_p.setFixedSize(28, 28)
            btn_p.setStyleSheet("color: #3498db; font-weight: bold; background: #fff; border: 1px solid #3498db; border-radius: 6px;")
            btn_p.clicked.connect(lambda _, f=fecha: self.editar_fecha_dialog(f, dialog))
            hbox.addWidget(lbl)
            hbox.addWidget(btn_x)
            hbox.addWidget(btn_p)
            item_widget = QWidget()
            item_widget.setLayout(hbox)
            vbox.addWidget(item_widget)
        self.actualizar_lista_fechas(dialog)
        dialog.exec_()
    
    # Eliminar y eidtar fechas desde la ventana

    def eliminar_fecha_dialog(self, fecha, dialog):
        if hasattr(self, "fechas_lectura"):
            self.fechas_lectura = [f for f in self.fechas_lectura if f[0] != fecha]
        self.actualizar_lista_fechas(dialog)

    def editar_fecha_dialog(self, fecha, dialog):
        # NO cierres el dialog aquí
        # Abre el calendario para editar la fecha
        def after_edit(nueva_fecha):
            # Actualiza la fecha en la lista
            for i, (f, w) in enumerate(self.fechas_lectura):
                if f == fecha:
                    self.fechas_lectura[i] = (nueva_fecha, w)
                    break
            # Actualiza la lista visual en el mismo dialog
            self.actualizar_lista_fechas(dialog)

        self.abrir_calendario_edicion(fecha, after_edit)
        # Limpi y actualiza la lsita de fechas

    def actualizar_lista_fechas(self, dialog):
        if dialog is None:
            return
        scroll = dialog.findChild(QScrollArea)
        if not scroll:
            return
        content = scroll.widget()
        if not content:
            return
        layout = content.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        # Vuelve a agregar las fechas
        for fecha, _ in getattr(self, "fechas_lectura", []):
            hbox = QHBoxLayout()
            lbl = QLabel(f"Datos Estacion Base - {fecha}")
            lbl.setObjectName("CampoPlomo")
            btn_x = QPushButton("X")
            btn_x.setFixedSize(28, 28)
            btn_x.setStyleSheet("color: red; font-weight: bold; background: #fff; border: 1px solid #3498db; border-radius: 6px;")
            btn_x.clicked.connect(lambda _, f=fecha: self.eliminar_fecha_dialog(f, dialog))
            btn_p = QPushButton("P")
            btn_p.setFixedSize(28, 28)
            btn_p.setStyleSheet("color: #3498db; font-weight: bold; background: #fff; border: 1px solid #3498db; border-radius: 6px;")
            btn_p.clicked.connect(lambda _, f=fecha: self.editar_fecha_dialog(f, dialog))
            hbox.addWidget(lbl)
            hbox.addWidget(btn_x)
            hbox.addWidget(btn_p)
            item_widget = QWidget()
            item_widget.setLayout(hbox)
            layout.addWidget(item_widget)
        
    def abrir_calendario_edicion(self, fecha_actual, callback):
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Fecha de Lectura")
        layout = QVBoxLayout(dialog)
        calendar = QCalendarWidget() # Usará el estilo por defecto del sistema
        layout.addWidget(calendar)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def aceptar():
            nueva_fecha = calendar.selectedDate().toString("yyyy-MM-dd")
            dialog.accept()
            callback(nueva_fecha)

        buttons.accepted.connect(aceptar)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()
            
    #actualiza botnoes de dias de lectura pg

    def actualizar_estado_botones_fechas(self):
        texto = self.num_dias.currentText()
        try:
            valor = int(texto)
        except ValueError:
            self.btn_ver_fechas.setEnabled(False)
            self.btn_fechas.setEnabled(False)
            return

        if valor < 2:
            self.btn_ver_fechas.setEnabled(False)
            self.btn_fechas.setEnabled(False)
        else:
            self.btn_ver_fechas.setEnabled(True)
            self.btn_fechas.setEnabled(True)
    
    def validar_fechas_pg(self):
        valor = int(self.num_dias.currentText())
        if valor < 2:
            mostrar_mensaje(self,"Aviso",
            "Este campo es solo para días superiores \na 1 día de lectura. Si es 1, la\n fecha se crea automáticamente.", QMessageBox.Information)
        
            return
        self.mostrar_calendario()
    
    def editar_fecha_lectura(self, item_widget, fecha):
        # Abre un calendario para seleccionar la nueva fecha
        dialog = QDialog(self)
        dialog.setWindowTitle("Editar Fecha de Lectura")
        layout = QVBoxLayout(dialog)        
        calendar = QCalendarWidget() # Usará el estilo por defecto del sistema
        layout.addWidget(calendar)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        def aceptar():
            nueva_fecha = calendar.selectedDate().toString("yyyy-MM-dd")
            dialog.accept()
            # Actualiza la fecha en la lista
            for i, (f, w) in enumerate(self.fechas_lectura):
                if f == fecha:
                    self.fechas_lectura[i] = (nueva_fecha, w)
                    break
            # Actualiza la lista visual
            self.actualizar_lista_fechas(dialog)

        buttons.accepted.connect(aceptar)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()
    
    def mostrar_mensaje_en_desarrollo(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Función no disponible")
        msg.setIcon(QMessageBox.Information)
        msg.setText("Funcionalidad en desarrollo.\nEsta función estará disponible próximamente.")
        msg.exec_()
    
    #ventana de formulario
    def abrir_dialogo_formulario(self):
        dialog = DialogoFormularios(self.controller, self)
        dialog.exec_()

    def pedir_licencia(self):
        dialog = LicenciaDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            nombre_usuario, licencia = dialog.get_datos()
            if not nombre_usuario or not licencia:
                QMessageBox.warning(self, "Licencia", "Debe ingresar su nombre y licencia para continuar.")
                return None, None
            if not ingresar_licencia(nombre_usuario, licencia):
                QMessageBox.warning(self, "Licencia inválida", "La licencia ingresada no es válida.")
                return None, None
            else:
                QMessageBox.information(self, "Licencia válida", "¡Gracias por activar el software!")
                return nombre_usuario, licencia
        return None, None