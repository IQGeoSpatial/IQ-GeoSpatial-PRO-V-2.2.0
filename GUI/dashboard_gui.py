import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QToolButton, QSizePolicy, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QSize
from utils.resource_path import resource_path
# La lógica de licencia ha sido eliminada.
from Controllers.dashboard_controller import DashboardController
from GUI.gnss_rinex_view import GNSSRinexView
from GUI.conversion_coordenadas_view import ConversionCoordenadasView
from GUI.validation_view import ValidationView
from GUI.help_view import HelpView

class DashboardApp(QWidget):
    def __init__(self):
        super().__init__()
        # Declarar los botones antes de init_ui para que existan
        self.btn_expediente = None
        self.btn_formularios = None
        self.btn_efemerides = None
        self.btn_pdf_converter = None
        self.theme_btn = None
        self.btn_placeholder2 = None # Botón para "Próximamente"

        self.controller = DashboardController(self)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("IQ GeoSpatial - Dashboard")
        logo_path = resource_path(os.path.join("Assets", "Image", "logo2.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        
        self.setMinimumSize(900, 700)
        self.setObjectName("DashboardWindow")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 40)
        main_layout.setSpacing(2) # Espaciado general entre elementos

        # --- Cabecera ---
        header_widget = self._crear_cabecera()
        main_layout.addWidget(header_widget)
        main_layout.addSpacing(6) # Espacio extra (margin-bottom) reducido

        # --- Grid de Botones ---
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # Fila 1
        self.btn_expediente = self._crear_boton_dashboard("carpeta.png", "Estructura", self.controller.mostrar_expediente, "Crear estructura de carpetas para un expediente.")
        self.btn_formularios = self._crear_boton_dashboard("formulario.png", "Formularios", self.controller.mostrar_formularios, "Generar formularios a partir de una plantilla Excel.")
        self.btn_efemerides = self._crear_boton_dashboard("efemeride.png", "Efemérides", self.controller.mostrar_efemerides, "Descargar efemérides precisas.")
        self.btn_pdf_converter = self._crear_boton_dashboard("convertPDF.png", "Convertir PDF", self.controller.mostrar_pdf_converter, "Convertir archivos Word a PDF.")

        grid_layout.addWidget(self.btn_expediente, 0, 0)
        grid_layout.addWidget(self.btn_formularios, 0, 1)
        grid_layout.addWidget(self.btn_efemerides, 0, 2)
        grid_layout.addWidget(self.btn_pdf_converter, 0, 3)

        # Fila 2 
        self.btn_validacion_expediente = self._crear_boton_dashboard("file_check.png", "Validación Expediente", self.mostrar_validation_view, "Validar la estructura y contenido del expediente.")
        self.btn_convertir_geografica_UTM = self._crear_boton_dashboard("conversioGeografica.png", "Convertir Geográfica a UTM", self.mostrar_conversion_coordenadas_view, "Convertir coordendas Geograficas (lat, Lon) a WGS-84 UTM.")
        self.btn_gnss_conversion_rinex = self._crear_boton_dashboard("convertirRinex.png", "Conversion a RINEX", self.mostrar_gnss_rinex_view, "Convertir datos GNSS a formato RINEX.")
        self.btn_ayuda_extra = self._crear_boton_dashboard("ayuda.png", "Ayuda", self.mostrar_help_view, "Ayuda y documentación.")

        grid_layout.addWidget(self.btn_validacion_expediente, 1, 0)
        grid_layout.addWidget(self.btn_convertir_geografica_UTM, 1, 1)
        grid_layout.addWidget(self.btn_gnss_conversion_rinex, 1, 2)
        grid_layout.addWidget(self.btn_ayuda_extra, 1, 3)

        # Fila 3 (botones deshabilitados)
        self.btn_youtube = self._crear_boton_dashboard("youtube.png", "Tutorial", self.controller.mostrar_video, "Ver tutorial en YouTube.")
        self.btn_placeholder2 = self._crear_boton_dashboard("add.png", "Módulo B", None, "Próximamente.", enabled=False)

        grid_layout.addWidget(self.btn_youtube, 2, 0)
        grid_layout.addWidget(self.btn_placeholder2, 2, 1)

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()
    
    # Funcionamiento de la ventana de converion de GNSS a RINEX
    def mostrar_gnss_rinex_view(self):
        self.gnss_rinex_window = GNSSRinexView()
        self.gnss_rinex_window.show()

    def mostrar_conversion_coordenadas_view(self):
        self.conversion_coordenadas_window = ConversionCoordenadasView()
        self.conversion_coordenadas_window.show()

    def mostrar_validation_view(self):
        self.validation_window = ValidationView()
        self.validation_window.show()

    def mostrar_help_view(self):
        self.help_window = HelpView()
        self.help_window.show()

    def _crear_cabecera(self):
        """Crea el widget de la cabecera con logo, título y slogan."""
        header_widget = QWidget()
        header_widget.setObjectName("Header")
        layout = QHBoxLayout(header_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Logo
        logo_label1 = QLabel()  # Primer QLabel para la mitad superior
        logo_label1.setStyleSheet("background: transparent;")
        logo_path = resource_path(os.path.join("Assets", "Icono", "icono.ico"))
        if os.path.exists(logo_path):
            original_pixmap = QPixmap(logo_path).scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Crear un pixmap con el efecto de difuminado superior
            faded_pixmap = QPixmap(original_pixmap.size())
            faded_pixmap.fill(Qt.transparent) # Empezar con un fondo transparente

            painter = QPainter(faded_pixmap)
            # 1. Dibuja la imagen original
            painter.drawPixmap(0, 0, original_pixmap)

            # 2. Prepara un gradiente para usar como máscara de opacidad
            gradient = QLinearGradient(0, 0, 0, faded_pixmap.height())
            gradient.setColorAt(0.0, QColor(0, 0, 0, 0))      # Totalmente transparente arriba
            gradient.setColorAt(0.4, QColor(0, 0, 0, 255))    # Se vuelve opaco
            gradient.setColorAt(1.0, QColor(0, 0, 0, 255))    # Permanece opaco hasta el final

            # 3. Aplica el gradiente como máscara (modo DestinationIn)
            painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
            painter.fillRect(faded_pixmap.rect(), gradient)
            painter.end()

            logo_label1.setPixmap(faded_pixmap)
        layout.addWidget(logo_label1, alignment=Qt.AlignTop)

        # Título y Slogan
        text_layout = QVBoxLayout()        
        text_layout.setSpacing(0) # Usaremos addSpacing para control manual
        title_label = QLabel("IQ GeoSpatial Pro")
        title_label.setObjectName("HeaderTitle")
        slogan_label = QLabel("Tu solución integral para la gestión de datos geodésicos.")
        slogan_label.setObjectName("HeaderSlogan")
        
        text_layout.addWidget(title_label)
        text_layout.addSpacing(10) # Espacio entre título y slogan
        text_layout.addWidget(slogan_label)

        # Botón de Detalles
        text_layout.addSpacing(15) # Espacio entre slogan y botón
        btn_detalles = QPushButton("DETALLES")
        btn_detalles.setObjectName("DetallesBtn")
        btn_detalles.setCursor(Qt.PointingHandCursor)
        text_layout.addWidget(btn_detalles, alignment=Qt.AlignLeft)

        text_layout.addStretch()

        layout.addLayout(text_layout, stretch=2)
        
        # Layout para botones de la esquina
        top_right_layout = QHBoxLayout()
        top_right_layout.setSpacing(10)

        # Botón de Tema
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("ThemeBtn")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self.controller.toggle_theme)
        top_right_layout.addWidget(self.theme_btn)

        # Botón de Informacion
        Info_btn = QPushButton("")
        Info_btn.setObjectName("Infobtn")
        Info_btn.setCursor(Qt.PointingHandCursor)

        info_icon_path = resource_path(os.path.join("Assets", "Image", "informacion.png"))
        if os.path.exists(info_icon_path):
            Info_btn.setIcon(QIcon(info_icon_path))
            Info_btn.setIconSize(QSize(24, 24))
        else:
            Info_btn.setText("i") # Texto alternativo si no se encuentra el icono

        Info_btn.clicked.connect(self.mostrar_informacion)
        top_right_layout.addWidget(Info_btn)

        layout.addLayout(top_right_layout)
        layout.setAlignment(top_right_layout, Qt.AlignTop)

        return header_widget


    def _crear_boton_dashboard(self, icon_name, text, callback, tooltip="", enabled=True):
        """Crea un QToolButton estilizado para el dashboard."""
        button = QToolButton()
        button.setText(text)
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)

        icon_path = resource_path(os.path.join("Assets", "Image", icon_name))
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(64, 64))
        
        if callback:
            button.clicked.connect(callback)
        
        button.setEnabled(enabled)
        return button
    
    # Actualizar cantidad de filas y columnas dashbboard segun tamaño de ventana
    def resizeEvent(self, event):
        super().resizeEvent(event)
        ancho = self.width()
        alto = self.height ()

        if ancho > 1800:
            columnas = 6
        elif 1200 < ancho <= 1800:
            columnas = 5
        elif 1000 <= ancho <= 1200:
            columnas = 4
        else:  # ancho < 800
            columnas = 3

        # Calcular espacio vertical en base al alto
        if alto > 1000:
            espacio_vertical = 40
        elif 700 < alto <= 1000:
            espacio_vertical = 25
        else:
            espacio_vertical = 10

        self._actualizar_columnas_dashboard(columnas, espacio_vertical)


    def _actualizar_columnas_dashboard(self, columnas, espacio_vertical=20):
        botones = [
            self.btn_expediente, self.btn_formularios, self.btn_efemerides,
            self.btn_pdf_converter, self.btn_validacion_expediente, self.btn_convertir_geografica_UTM,
            self.btn_gnss_conversion_rinex, self.btn_ayuda_extra, self.btn_youtube
        ]
        grid_layout = self.findChild(QGridLayout)
        if grid_layout:
            grid_layout.setVerticalSpacing(espacio_vertical)

            while grid_layout.count():
                item = grid_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            
            for idx, btn in enumerate(botones):
                if btn:
                    fila = idx // columnas
                    col = idx % columnas
                    grid_layout.addWidget(btn, fila, col)


    def mostrar_informacion(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Información")
        msg.setIcon(QMessageBox.Information) # El estilo se hereda del tema global
        msg.setText(
            '<span style="color:#e53935;"><b>IQ GeoSpatial Pro</b></span><br><br>'
            'Version: 2.2.0<br>'
            'Date: 2025-08-24<br>'
            'WhatsApp: <a href="https://wa.me/51900102921">+51 900 102 921</a><br>'
            '<span style="color:#e53935;">Support:</span> iqgeospatial@gmail.com'
        )
        msg.exec_()
    
    def mostrar_funcion_en_desarrollo(self):
        QMessageBox.information(self, "Función en desarrollo", "Esta función está en desarrollo y estará disponible próximamente.")