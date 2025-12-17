from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QComboBox,
    QCheckBox, QGroupBox, QGridLayout, QSizePolicy, QFrame, QScrollArea, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont, QIcon  
from PyQt5.QtCore import Qt, QSize  
from Controllers.gnss_rinex_controller import GNSSRinexController
from utils.resource_path import resource_path
import os

# Diccionario de marcas y modelos reconocidos por RTKLIB
RTKLIB_BRANDS_MODELS = {
    "u-blox": ["NEO", "ZED", "Todos los módulos"],
    "NovAtel": ["OEM4", "OEMV", "OEM6", "OEM7"],
    "Septentrio": ["SBF"],
    "Javad": ["JPS"],
    "Topcon": ["TPS"],
    "Hemisphere": ["BIN", "Similares"],
    "Skytraq": ["Chipsets GNSS"],
    "ComNav / SinoGNSS": ["OBS"],
    "NVS Technologies": ["BIN"],
    "IGS / RINEX existentes": ["RINEX"],
    "Otro": []
}

class GNSSRinexView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = GNSSRinexController(self)
        self.archivo_gnss = ""
        self.archivo_efemeride = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Convertir GNSS a RINEX")
        self.setWindowIcon(QIcon(resource_path("Assets/Image/convertirRinex.png")))
        self.setMinimumSize(700, 500)
        self.setMaximumSize(700, 500) 
        self.setFixedSize(700, 500)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 5, 0, 10)

        self.setStyleSheet("background: #f4f6fa; border: none;")  

        titulo = QLabel("Convertir GNSS a RINEX")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #2c437c; "
            "margin-top: 1px; margin-bottom: 1px; padding-top: 0px; padding-bottom: 0px;"
        )
        main_layout.addWidget(titulo)
        main_layout.addSpacing(30)  

        # --- Scroll area para los grupos ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Sin scroll al inicio

        self.grupos_container = QWidget()
        self.grupos_container.setStyleSheet("background: transparent; border: none;")
        self.grupos_layout = QVBoxLayout(self.grupos_container)
        self.grupos_layout.setSpacing(10)
        self.grupos_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.grupos_container)
        main_layout.addWidget(self.scroll_area)

        # --- Define combo_style antes de usarlo ---
        combo_style = """
            QComboBox {
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 12px;
                background: transparent;
                border: 1px solid #b0c4de;
                min-width: 70px;
            }
            QComboBox::drop-down {
                border-radius: 10px;
                border: none;
            }
        """

        # --- Define chk_style antes de usarlo ---
        chk_style = """
            QCheckBox {
                spacing: 8px;
                font-size: 12px;
                border-radius: 9px;
                padding: 2px 6px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #2c437c;
                background: #fff;
            }
            QCheckBox::indicator:checked {
                background: #2c437c;
                border: 2px solid #2c437c;
            }
        """

        # Inicializa con el primer grupo
        self.grupos = []
        self.combo_style = combo_style  
        self.chk_style = chk_style      
        self.agregar_grupo(primero=True)

        # --- CREA EL GRID ANTES DE USARLO ---
        grid = QGridLayout()
        grid.setHorizontalSpacing(0)
        grid.setVerticalSpacing(8)

        # --- Fila 1: RINEX Configuración y Output centrados en la ventana ---
        rinex_row = QHBoxLayout()
        rinex_row.setSpacing(30)

        rinex_group = QGroupBox("RINEX Configuración")
        rinex_group.setStyleSheet("font-size: 12px;")
        rinex_layout = QGridLayout()
        rinex_layout.setHorizontalSpacing(8)
        rinex_layout.setVerticalSpacing(4)
        self.combo_rinex_version = QComboBox()
        self.combo_rinex_version.addItems([
            "2.11",
            "3.02",
            "3.03",
            "3.04"
        ])
        self.combo_rinex_version.setStyleSheet(combo_style)
        rinex_layout.addWidget(QLabel("RINEX Version"), 0, 0)
        rinex_layout.addWidget(self.combo_rinex_version, 0, 1)
        self.combo_interval = QComboBox()
        self.combo_interval.addItems(["1s", "5s", "10s", "30s"])
        self.combo_interval.setStyleSheet(combo_style)
        rinex_layout.addWidget(QLabel("Intervalo de Lectura"), 1, 0)
        rinex_layout.addWidget(self.combo_interval, 1, 1)
        rinex_group.setLayout(rinex_layout)
        rinex_row.addWidget(rinex_group)

        output_group = QGroupBox("Salida")
        output_group.setStyleSheet("font-size: 12px;")
        output_layout = QVBoxLayout()
        self.chk_obs = QCheckBox("Observación (.obs)")
        self.chk_obs.setChecked(True)
        self.chk_obs.setStyleSheet(chk_style)
        self.chk_nav = QCheckBox("Navevación (.nav)")
        self.chk_nav.setChecked(True)
        self.chk_nav.setStyleSheet(chk_style)
        output_layout.addWidget(self.chk_obs)
        output_layout.addWidget(self.chk_nav)
        output_group.setLayout(output_layout)
        rinex_row.addWidget(output_group)

        rinex_row_widget = QWidget()
        rinex_row_widget.setLayout(rinex_row)
        grid.addWidget(rinex_row_widget, 1, 0, 1, 4, alignment=Qt.AlignCenter)

        # --- Fila 2: Botón Convertir centrado ---
        btn_convertir = QPushButton("Convertir")
        btn_convertir.setStyleSheet("""
            QPushButton {
                background: #2c437c;
                color: white;
                font-weight: bold;
                padding: 8px 24px;
                border-radius: 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #1a2a4c;
            }
        """)
        btn_convertir.setFixedWidth(120)
        btn_convertir.setFixedHeight(36)
        btn_convertir.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn_convertir.clicked.connect(self.convertir)
        grid.addWidget(btn_convertir, 2, 0, 1, 4, alignment=Qt.AlignHCenter)

        # --- Fila 3: Resultado ---
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("font-size: 12px;")
        grid.addWidget(self.result_label, 3, 0, 1, 4)

        main_layout.addLayout(grid)

        # --- Mensaje de bienvenida y estado Beta ---
        msg_box = QMessageBox(self)
        icon_pixmap = QPixmap(resource_path("Assets/Image/ConvertirRinex.png")).scaled(
            64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        msg_box.setIconPixmap(icon_pixmap)
        msg_box.setWindowTitle("Función en Desarrollo (Beta)")
        msg_box.setText("Bienvenido al conversor de GNSS a RINEX. Esta herramienta está basada en la utilidad `rnxcnv` de RTKLIB y se encuentra en fase de desarrollo. Agradecemos tus comentarios para mejorarla.")

        info_text = "<b>Formatos y receptores soportados:</b><br><ul>"
        for brand, models in RTKLIB_BRANDS_MODELS.items():
            if models:
                info_text += f"<li><b>{brand}:</b> {', '.join(models)}</li>"
            else:
                info_text += f"<li><b>{brand}</b></li>"
        info_text += "</ul><br><i>Si tu formato no está en la lista, puedes intentar la conversión de todas formas, ya que RTKLIB podría reconocerlo.</i>"

        msg_box.setInformativeText(info_text)

        # Botón personalizado "Aceptar"
        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background: #2c437c; color: white; font-weight: bold;
                padding: 6px 20px; border-radius: 12px; font-size: 12px;
            }
            QPushButton:hover { background: #1a2a4c; }
        """)
        msg_box.addButton(btn_aceptar, QMessageBox.AcceptRole)

        msg_box.exec_()

    # Cargar archivo GNSS
    def cargar_archivo_gnss(self, label_gnss):
        archivo, _ = QFileDialog.getOpenFileName(self, "Selecciona archivo GNSS")
        if archivo:
            label_gnss.archivo = archivo  # Guarda la ruta en el label

    # Cargar archivo .nav
    def cargar_archivo_nav(self, label_nav):
        archivo, _ = QFileDialog.getOpenFileName(self, "Selecciona archivo Efeméride")
        if archivo:
            label_nav.archivo = archivo  # Guarda la ruta en el label

    # Metodo para la conversion de GNSS a RINEX
    def convertir(self):
        carpeta_salida = QFileDialog.getExistingDirectory(self, "Selecciona carpeta de destino")
        opciones = {
            "rinex_version": self.combo_rinex_version.currentText(),
            "interval": self.combo_interval.currentText().replace("s", ""),
            "output_obs": self.chk_obs.isChecked(),
            "output_nav": self.chk_nav.isChecked(),
            "output_dir": carpeta_salida
        }
        archivos_gnss = self.grupos[0].archivos_gnss  # <-- Envía todos los archivos seleccionados
        archivos = {
            "data": archivos_gnss,
            "nav": []
        }
        print("arrrr: ", archivos)
        self.controller.convertir_gnss_a_rinex(archivos, opciones)

    # Muestra la ruta de conversion exitosa
    def mostrar_resultado_conversion(self, resultado):
        if resultado["success"]:
            self.result_label.setText("Conversión exitosa. Archivos en: " + resultado["output_dir"])
        else:
            self.result_label.setText("Error: " + resultado["message"])

    def agregar_grupo(self, primero=False):
        grupo_widget = QWidget()
        grupo_widget.setFixedHeight(220)
        grupo_widget.setStyleSheet("background: transparent; border: none;")
        grupo_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # <-- Expande horizontal

        grupo_vbox = QVBoxLayout(grupo_widget)
        grupo_vbox.setSpacing(8)
        grupo_vbox.setContentsMargins(0, 0, 0, 0)
        grupo_vbox.setAlignment(Qt.AlignCenter)

        # --- Icono GNSS centrado, sin borde ---
        btn_gnss_icon = QPushButton()
        btn_gnss_icon.setIcon(QIcon(QPixmap(resource_path("Assets/Image/archivo1.png"))))
        btn_gnss_icon.setIconSize(QSize(64, 72))
        btn_gnss_icon.setFixedSize(70, 80)
        btn_gnss_icon.setStyleSheet("border: none; background: transparent;")
        grupo_vbox.addWidget(btn_gnss_icon, alignment=Qt.AlignCenter)

        # --- Botón para cargar archivos o carpeta ---
        btn_cargar = QPushButton("Cargar archivo/carpeta GNSS")
        btn_cargar.setStyleSheet("""
            QPushButton {
                background: #2c437c;
                color: white;
                font-size: 13px;
                border-radius: 10px;
                padding: 4px 16px;
            }
            QPushButton:hover {
                background: #1a2a4c;
            }
        """)
        grupo_vbox.addWidget(btn_cargar, alignment=Qt.AlignCenter)

        # --- Scroll area para archivos, más ancho ---
        archivos_scroll = QScrollArea()
        archivos_scroll.setWidgetResizable(True)
        archivos_scroll.setFixedHeight(110)
        archivos_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #f4f6fa;
                width: 12px;
                margin: 2px 2px 2px 2px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #2c437c;
                min-height: 24px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
                border: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        archivos_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # <-- Expande horizontal
        archivos_scroll.setMinimumWidth(650)  # <-- Más ancho el área del scroll
        grupo_vbox.addWidget(archivos_scroll, alignment=Qt.AlignCenter)

        archivos_widget = QWidget()
        archivos_widget.setStyleSheet("background: transparent; border: none;")
        archivos_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # <-- Expande horizontal
        archivos_widget.setMinimumWidth(650)  # <-- Más ancho el contenido del scroll
        archivos_grid = QGridLayout(archivos_widget)
        archivos_grid.setHorizontalSpacing(20)
        archivos_grid.setVerticalSpacing(4)
        archivos_scroll.setWidget(archivos_widget)

        self.grupos_layout.addWidget(grupo_widget)
        self.grupos.append(grupo_widget)

        grupo_widget.archivos_gnss = []
        grupo_widget.archivos_nav = []

        def mostrar_archivos():
            while archivos_grid.count():
                item = archivos_grid.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            for i, archivo_gnss in enumerate(grupo_widget.archivos_gnss):
                nombre_gnss = os.path.basename(archivo_gnss)
                label_gnss = QLabel(nombre_gnss)
                label_gnss.setStyleSheet("color: #2c437c; font-size: 13px; text-decoration: underline; background: transparent;")
                label_gnss.setAlignment(Qt.AlignCenter)  # <-- Centra el texto

                label_gnss.archivo = archivo_gnss
                label_gnss.mousePressEvent = lambda event, l=label_gnss: self.mostrar_info_archivo(l)

                btn_x = QPushButton("✕")
                btn_x.setFixedSize(24, 24)
                btn_x.setStyleSheet("""
                    QPushButton {
                        font-size: 13px;
                        background: #f44336;
                        color: white;
                        border-radius: 12px;
                        border: 1px solid #c62828;
                    }
                    QPushButton:hover {
                        background: #c62828;
                        color: #fff;
                        border: 1px solid #f44336;
                    }
                """)
                def eliminar_fila(idx=i):
                    if idx < len(grupo_widget.archivos_gnss):
                        grupo_widget.archivos_gnss.pop(idx)
                    mostrar_archivos()
                btn_x.clicked.connect(eliminar_fila)

                # Crea un layout horizontal para centrar ambos elementos
                fila_layout = QHBoxLayout()
                fila_layout.addStretch(1)
                fila_layout.addWidget(label_gnss)
                fila_layout.addSpacing(12)
                fila_layout.addWidget(btn_x)
                fila_layout.addStretch(1)

                # Crea un widget contenedor para la fila
                fila_widget = QWidget()
                fila_widget.setLayout(fila_layout)

                archivos_grid.addWidget(fila_widget, i, 0, 1, 2, alignment=Qt.AlignCenter)

        def cargar_archivos():
            opciones = QFileDialog.Options()
            archivos, _ = QFileDialog.getOpenFileNames(
                self,
                "Selecciona archivos GNSS",
                "",
                "Archivos GNSS (*.dat *.ubx *.bin *.jps *.sbf *.tps *.hcn *.T01 *.chc);;Todos los archivos (*.*)",
                options=opciones
            )
            # Agrega los nuevos archivos sin borrar los anteriores
            for archivo in archivos:
                if archivo not in grupo_widget.archivos_gnss:
                    grupo_widget.archivos_gnss.append(archivo)
            mostrar_archivos()

        btn_gnss_icon.clicked.connect(cargar_archivos)
        btn_cargar.clicked.connect(cargar_archivos)