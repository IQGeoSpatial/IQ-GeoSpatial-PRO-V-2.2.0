from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QLabel, QPushButton, QGroupBox,
    QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QFrame, QGridLayout, QComboBox, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtGui import QIcon
from utils.resource_path import resource_path  
from utils.map_utils import este_norte_a_latlon
from Controllers.conversion_coordenadas_controller import ConversionCoordenadasController
import folium, tempfile, os
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pandas as pd

try:
    import simplekml
except ImportError:
    simplekml = None

SISTEMAS = [
    ("Elipsoidal", ["Latitud", "Longitud", "Altitud"]),
    ("UTM", ["Este", "Norte", "Altitud"]),
]

class ConversionCoordenadasView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Conversión de Coordenadas")
        self.setMinimumSize(1300, 850)
        self.controller = ConversionCoordenadasController(self)
        self.puntos_convertidos = []  # Lista para almacenar los puntos convertidos

        self.setWindowIcon(QIcon(resource_path(os.path.join("Assets", "Image", "conversioGeografica.png"))))  # Ícono de la ventana

        main_layout = QHBoxLayout(self)

        # --- Panel Izquierdo para Controles ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Layout para las dos columnas de Origen y Destino
        columnas_tablas_layout = QHBoxLayout()

        # --- Origen ---
        origen_layout = QVBoxLayout()
        self.origen_radios = []
        radios_layout = QGridLayout()
        for i, (sistema, _) in enumerate(SISTEMAS):
            radio = QRadioButton(sistema)
            radio.toggled.connect(self.mostrar_campos_origen)
            self.origen_radios.append(radio)
            radios_layout.addWidget(radio, i // 3, i % 3)
        origen_layout.addLayout(radios_layout)

        self.origen_campos_frame = QFrame()
        self.origen_campos_layout = QGridLayout(self.origen_campos_frame)
        origen_layout.addWidget(self.origen_campos_frame)

        # Combo zona para UTM manual (reemplazado por QLineEdit)
        self.zona_origen_lineedit = QLineEdit()
        self.zona_origen_lineedit.setVisible(False)  
        self.zona_origen_lineedit.setPlaceholderText("Zona") 
        self.zona_origen_lineedit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e3ea;
                border-radius: 10px;
                padding: 8px 6px;
                background: #fff;
                font-size: 12px;
                color: #222b45;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
                background: #f5faff;
            }
        """)

        # Crear el QLineEdit para la zona de destino UNA SOLA VEZ aquí
        self.zona_destino_lineedit = QLineEdit()
        self.zona_destino_lineedit.setReadOnly(True)
        self.zona_destino_lineedit.setVisible(False) # Oculto por defecto
        self.zona_destino_lineedit.setStyleSheet("""
            QLineEdit { border: 2px solid #e0e3ea; border-radius: 10px; padding: 8px 6px; background: #fff; font-size: 12px; color: #222b45; }
            QLineEdit:focus { border: 2px solid #3b82f6; background: #f5faff; }
        """)
        self.zona_destino_lineedit.setPlaceholderText("Zona")

        self.btn_cargar_excel_origen = QPushButton("Importar Puntos")
        self.btn_cargar_excel_origen.setIcon(QIcon(resource_path(os.path.join("Assets", "Image", "upload_excel.png"))))  # Ícono de subir
        self.btn_cargar_excel_origen.setIconSize(QSize(40, 43))  
        self.btn_cargar_excel_origen.setToolTip("Importar puntos") 
        self.btn_cargar_excel_origen.setStyleSheet("""
            QPushButton {
                background-color: transparent;  /* Fondo oscuro */
                border: none;
                border-radius: 8px;  /* Bordes redondeados */
                margin-top: 5px;  /* Reducir margen superior */
                margin-bottom: 5px;  /* Reducir margen inferior */
                padding: 10px;  /* Espaciado interno */
                color: #000000;
            }
        """)
        self.btn_cargar_excel_origen.clicked.connect(self.cargar_excel_origen)
        origen_layout.addWidget(self.btn_cargar_excel_origen)

        self.tabla_origen = QTableWidget()
        self.tabla_origen.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tabla_origen.verticalHeader().setFixedWidth(30)
        self.tabla_origen.horizontalHeader().setStretchLastSection(False)

        origen_controls_widget = QWidget()
        origen_controls_widget.setLayout(origen_layout)
        origen_controls_widget.setFixedWidth(260)
        columnas_tablas_layout.addWidget(origen_controls_widget)

        # --- Destino ---
        destino_layout = QVBoxLayout()
        self.destino_radios = []
        radios_layout_destino = QGridLayout()
        for i, (sistema, _) in enumerate(SISTEMAS):
            radio = QRadioButton(sistema)
            radio.toggled.connect(self.mostrar_campos_destino)
            self.destino_radios.append(radio)
            radios_layout_destino.addWidget(radio, i // 3, i % 3)
        destino_layout.addLayout(radios_layout_destino)

        self.destino_campos_frame = QFrame()
        self.destino_campos_layout = QGridLayout(self.destino_campos_frame)
        destino_layout.addWidget(self.destino_campos_frame)

        # --- Botón de exportar puntos con ícono ---
        self.btn_exportar_puntos = QPushButton("Exportar Puntos")
        self.btn_exportar_puntos.setIcon(QIcon(resource_path(os.path.join("Assets", "Image", "download_excel.png")))) 
        self.btn_exportar_puntos.setIconSize(QSize(40, 40))  
        self.btn_exportar_puntos.setToolTip("Exportar puntos")  
        self.btn_exportar_puntos.setStyleSheet("""
            QPushButton {
                background-color: transparent;  /* Fondo oscuro */
                border: none;
                border-radius: 8px;  /* Bordes redondeados */
                margin-top: 5px;  /* Reducir margen superior */
                margin-bottom: 5px;  /* Reducir margen inferior */
                padding: 10px;  /* Espaciado interno */
                color: #000000;
            }
        """)
        self.btn_exportar_puntos.clicked.connect(self.exportar_puntos_destino)
        destino_layout.addWidget(self.btn_exportar_puntos)

        self.tabla_destino = QTableWidget()
        self.tabla_destino.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tabla_destino.verticalHeader().setFixedWidth(30)
        self.tabla_destino.horizontalHeader().setStretchLastSection(False)

        destino_controls_widget = QWidget()
        destino_controls_widget.setLayout(destino_layout)
        destino_controls_widget.setFixedWidth(260)
        columnas_tablas_layout.addWidget(destino_controls_widget)

        left_layout.addLayout(columnas_tablas_layout)

        titulo_tabla_origen = QLabel("Tabla de Origen")
        titulo_tabla_origen.setObjectName("tableTitle")
        left_layout.addWidget(titulo_tabla_origen)
        left_layout.addWidget(self.tabla_origen)

        titulo_tabla_destino = QLabel("Tabla de Destino")
        titulo_tabla_destino.setObjectName("tableTitle")
        left_layout.addWidget(titulo_tabla_destino)
        left_layout.addWidget(self.tabla_destino)

        botones_layout = QHBoxLayout()
        self.btn_convertir = QPushButton("Convertir")
        self.btn_convertir.clicked.connect(self.convertir_coordenadas)
        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_campos)
        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_convertir)
        botones_layout.addSpacing(20)
        botones_layout.addWidget(self.btn_limpiar)
        botones_layout.addStretch()
        left_layout.addLayout(botones_layout)

        main_layout.addWidget(left_panel)

        # --- Mapa (ocupa todo el lado derecho) ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.mapa_view = QWebEngineView()
        right_layout.addWidget(self.mapa_view)
        main_layout.addWidget(right_panel, stretch=1)

        # --- Controles sobre el mapa ---
        self.combo_simbolo = QComboBox(right_panel)  # El padre es el panel contenedor
        self.combo_simbolo.setObjectName("mapSymbolComboBox")
        self.combo_simbolo.addItems(['Triángulo','Círculo', 'Cuadrado', 'Cruz', 'Estrella', 'Pin'])
        self.combo_simbolo.setToolTip("Seleccionar símbolo del marcador")
        self.combo_simbolo.currentTextChanged.connect(lambda: self.cargar_mapa_base())
        self.combo_simbolo.show()
        self.combo_simbolo.raise_()

        self.origen_radios[0].setChecked(True)
        self.destino_radios[0].setChecked(True)

        # Carga un mapa base al iniciar
        self.cargar_mapa_base()
        self.aplicar_estilo_moderno()

    def resizeEvent(self, event):
        """Asegura que los controles sobre el mapa se reposicionen correctamente."""
        super().resizeEvent(event)
        if hasattr(self, 'combo_simbolo') and self.combo_simbolo.parentWidget():
            parent_width = self.combo_simbolo.parentWidget().width()
            margin_y = 10
            
            combo_size = self.combo_simbolo.sizeHint()
            combo_x = (parent_width - combo_size.width()) // 2
            
            self.combo_simbolo.move(combo_x, margin_y)

    def cargar_mapa_base(self, lat=-12, lon=-77, zoom=6):
        # Crear el mapa base con un zoom máximo más alto y varias capas
        m = folium.Map(location=[lat, lon], zoom_start=zoom, max_zoom=20)

        tooltip_container_style = "<style>.leaflet-tooltip { background: transparent !important; border: none !important; box-shadow: none !important; } .leaflet-tooltip-tip { display: none !important; }</style>"
        m.get_root().header.add_child(folium.Element(tooltip_container_style))

        # Añadir varias capas de mapas para que el usuario elija desde el mapa
        folium.TileLayer('OpenStreetMap', name='Estándar (OpenStreetMap)').add_to(m)
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Satélite (Esri)",
            overlay=False
        ).add_to(m)
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            attr="Google",
            name="Satélite (Google)",
            overlay=False
        ).add_to(m)
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            attr="Google",
            name="Estándar (Google)",
            overlay=False
        ).add_to(m)

        # Añadir norte magnético
        north_arrow_html = """
            <div style="position: fixed; top: 80px; right: 20px; z-index: 1000; text-align: center; font-family: sans-serif; pointer-events: none;">
                <div style="font-size: 24px; font-weight: bold; color: #FFFF00;">N</div>
                <svg width="40" height="50" viewbox="0 0 100 100" style="filter: drop-shadow(2px 2px 2px rgba(0,0,0,0.3));">
                    <path d="M 50 5 L 85 95 L 50 70 L 15 95 Z" style="fill:#000000; stroke:#FFFF00; stroke-width:8; stroke-linejoin:round;" />
                </svg>
            </div>
        """
        m.get_root().html.add_child(folium.Element(north_arrow_html))

        # Añadir el control para cambiar de capa directamente en el mapa
        folium.LayerControl().add_to(m)

        # Volver a agregar los puntos convertidos al mapa
        if hasattr(self, "puntos_convertidos") and self.puntos_convertidos:
            simbolo_seleccionado = self.combo_simbolo.currentText() if hasattr(self, 'combo_simbolo') else 'Círculo'
            for lat, lon, nombre in self.puntos_convertidos:
                # Crear el marcador según el símbolo seleccionado
                if simbolo_seleccionado == 'Círculo':
                    marker = folium.CircleMarker(location=[lat, lon], radius=7, color='#cc0000', weight=2, fill=True, fill_color='#ff3333', fill_opacity=0.8, popup=nombre)
                elif simbolo_seleccionado == 'Triángulo':
                    marker = folium.RegularPolygonMarker(location=[lat, lon], number_of_sides=3, radius=10, rotation=0, color='#cc0000', fill_color='#ff3333', fill_opacity=0.8, popup=nombre)
                elif simbolo_seleccionado == 'Cuadrado':
                    marker = folium.RegularPolygonMarker(location=[lat, lon], number_of_sides=4, radius=9, rotation=45, color='#cc0000', fill_color='#ff3333', fill_opacity=0.8, popup=nombre)
                elif simbolo_seleccionado == 'Cruz':
                    marker = folium.Marker(location=[lat, lon], popup=nombre, icon=folium.DivIcon(html=f"""<div style="font-size: 24px; font-weight: bold; color: #ff3333; position: relative; left: -12px; top: -12px; text-shadow: 1px 1px 2px #000;">+</div>"""))
                elif simbolo_seleccionado == 'Estrella':
                    marker = folium.Marker(location=[lat, lon], popup=nombre, icon=folium.DivIcon(html=f"""<div style="font-size: 28px; color: #ff3333; position: relative; left: -14px; top: -14px; text-shadow: 1px 1px 2px #000;">★</div>"""))
                else: # Pin
                    marker = folium.Marker(location=[lat, lon], popup=nombre, icon=folium.Icon(color='red', icon='info-sign'))

                # Estilo para la etiqueta del nombre
                tooltip_style = """
                    background-color: #ffff00;
                    border: 1px solid #555;
                    border-radius: 10px;
                    color: black;
                    font-size: 12px;  /* Aumentar el tamaño de la fuente */
                    font-weight: bold;
                    padding: 5px 10px;  /* Ajustar el espaciado interno */
                    box-shadow: 2px 2px 3px rgba(0,0,0,0.4);
                    white-space: nowrap;  /* Evitar que el texto se divida en varias líneas */
                """
                folium.Tooltip(
                    text=f"<b>{nombre}</b>",
                    permanent=True,
                    direction='auto',
                    style=tooltip_style
                ).add_to(marker)
                marker.add_to(m)

        # Guardar el mapa en un archivo temporal y mostrarlo
        temp_html = tempfile.NamedTemporaryFile(suffix=".html", delete=False).name
        m.save(temp_html)
        self.mapa_view.setUrl(QUrl.fromLocalFile(temp_html))

    def _configurar_panel_coordenadas(self, panel_type, radios, layout, tabla):
        """Configura dinámicamente un panel de coordenadas (origen o destino)."""
        if panel_type == 'origen':
            self.zona_origen_lineedit.setParent(None)
        self.zona_destino_lineedit.setParent(None)

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 2. Determinar sistema y campos correspondientes
        sistema = next((r.text() for r in radios if r.isChecked()), SISTEMAS[0][0])
        campos_labels = next((c for s, c in SISTEMAS if s == sistema), [])

        # 3. Crear y añadir los QLineEdit para los campos
        campos_widgets = []
        for i, label in enumerate(campos_labels):
            layout.addWidget(QLabel(label), i, 0)
            campo = QLineEdit()
            if panel_type == 'destino':
                campo.setReadOnly(True)
            else:  
                campo.setReadOnly(False) 

            if label == "Altitud" and sistema == "UTM":
                layout.addWidget(campo, i, 1)
            else:
                layout.addWidget(campo, i, 1, 1, 3)

            campos_widgets.append(campo)

        setattr(self, f"{panel_type}_campos", campos_widgets)

        # 4. Lógica específica para UTM: añadir Zona al lado de Altitud
        if sistema == "UTM":
            try:
                altura_index = campos_labels.index("Altitud")
                if panel_type == 'origen':
                    layout.addWidget(QLabel("Zona:"), altura_index, 2)
                    layout.addWidget(self.zona_origen_lineedit, altura_index, 3)
                    self.zona_origen_lineedit.setVisible(True)
                    self.zona_origen_lineedit.setFixedWidth(60) 
                    campos_widgets[altura_index].setFixedWidth(60)  
                else:  
                    layout.addWidget(QLabel("Zona:"), altura_index, 2)
                    layout.addWidget(self.zona_destino_lineedit, altura_index, 3)
                    self.zona_destino_lineedit.setVisible(True)
                    self.zona_destino_lineedit.setFixedWidth(60)
                    campos_widgets[altura_index].setFixedWidth(60)  
            except ValueError:
                pass
        elif panel_type == 'origen':
            self.zona_origen_lineedit.setVisible(False)
        self.zona_destino_lineedit.setVisible(sistema == "UTM" and panel_type == 'destino')

        # 5. Configurar las columnas de la tabla correspondiente
        columnas_tabla = ["Nombre"] + campos_labels
        if panel_type == 'destino' and sistema == "UTM":
            columnas_tabla.append("Zona")

        tabla.setColumnCount(len(columnas_tabla))
        tabla.setHorizontalHeaderLabels(columnas_tabla)
        for i in range(tabla.columnCount()):
            tabla.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)

    def mostrar_campos_origen(self):
        self._configurar_panel_coordenadas('origen', self.origen_radios, self.origen_campos_layout, self.tabla_origen)

    def mostrar_campos_destino(self):
        self._configurar_panel_coordenadas('destino', self.destino_radios, self.destino_campos_layout, self.tabla_destino)

    # Cargar datos desde un Excel a la tabla de origen
    def cargar_excel_origen(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Selecciona archivo Excel", "", "Archivos Excel (*.xlsx *.xls)")
        if archivo:
            df = pd.read_excel(archivo)
            # Ajusta los nombres de columnas según tu archivo
            columnas_tabla = list(df.columns)
            self.tabla_origen.setRowCount(len(df))
            self.tabla_origen.setColumnCount(len(columnas_tabla))
            self.tabla_origen.setHorizontalHeaderLabels(columnas_tabla)
            for i, fila in df.iterrows():
                for j, valor in enumerate(fila):
                    valor_str = ""
                    if pd.notna(valor):
                        if j == 0:
                            try:
                                # Intenta convertir a float y luego a int para eliminar decimales innecesarios (ej. 1.0 -> 1)
                                valor_str = str(int(float(valor)))
                            except (ValueError, TypeError):
                                valor_str = str(valor)
                        else:
                            valor_str = str(valor)
                    
                    self.tabla_origen.setItem(i, j, QTableWidgetItem(valor_str))

    # convertir las coordenadas
    def convertir_coordenadas(self):
        
        try:
            sistema_origen = next((r.text() for r in self.origen_radios if r.isChecked()), None)
            sistema_destino = next((r.text() for r in self.destino_radios if r.isChecked()), None)

            if sistema_origen == sistema_destino:
                QMessageBox.warning(self, "Conversión no permitida", "No se puede convertir porque el sistema de origen y destino son iguales.")
                return

            if self.tabla_origen.rowCount() > 0:
                for campo in getattr(self, "destino_campos", []):
                    campo.clear()
                if hasattr(self, "zona_destino_lineedit"):
                    self.zona_destino_lineedit.clear()

                resultados = []
                nombres = []

                # Si el origen es UTM, se obtiene la zona del QLineEdit una sola vez.
                zona_utm_origen = ""
                if sistema_origen == "UTM":
                    zona_utm_origen = self.zona_origen_lineedit.text().strip()
                    if not zona_utm_origen:
                        QMessageBox.warning(self, "Zona Requerida", "Para la conversión por lote desde UTM, por favor ingrese la Zona de origen.")
                        return

                for i in range(self.tabla_origen.rowCount()):
                    nombre = self.tabla_origen.item(i, 0).text() if self.tabla_origen.item(i, 0) else ""
                    nombres.append(nombre)

                    # Construir la lista de valores para el controlador, igual que en la conversión manual
                    valores_fila = [
                        self.tabla_origen.item(i, 1).text() if self.tabla_origen.item(i, 1) else "", # Coord 1 (Lat/Este)
                        self.tabla_origen.item(i, 2).text() if self.tabla_origen.item(i, 2) else "", # Coord 2 (Lon/Norte)
                        self.tabla_origen.item(i, 3).text() if self.tabla_origen.item(i, 3) else ""  # Coord 3 (Altitud)
                    ]

                    if sistema_origen == "UTM":
                        valores_fila.append(zona_utm_origen)

                    resultado_fila = self.controller.convertir(sistema_origen, sistema_destino, valores_fila)
                    resultados.append(resultado_fila)

                self.tabla_destino.setRowCount(len(resultados))
                for i, fila in enumerate(resultados):
                    nombre = nombres[i]
                    if sistema_destino == "Elipsoidal":
                        # Para Elipsoidal: [Latitud, Longitud, Altitud]
                        latitud = fila[0] if len(fila) > 0 else ""
                        longitud = fila[1] if len(fila) > 1 else ""
                        altura = fila[2] if len(fila) > 2 else ""
                        fila_destino = [nombre, latitud, longitud, altura]
                    elif sistema_destino == "UTM":
                        # Para UTM: [Este, Norte, Zona, Letra, Altitud]
                        este = fila[0] if len(fila) > 0 else ""
                        norte = fila[1] if len(fila) > 1 else ""
                        zona = fila[2] if len(fila) > 2 else ""
                        letra = fila[3] if len(fila) > 3 else ""
                        altura = fila[4] if len(fila) > 4 else ""
                        fila_destino = [nombre, este, norte, altura, zona]
                    else:
                        fila_destino = [nombre] + ["Error"] * len(fila)

                    for j, valor in enumerate(fila_destino):
                        self.tabla_destino.setItem(i, j, QTableWidgetItem(str(valor)))
            else:
                self.tabla_destino.setRowCount(0)
                # Convierte el punto manual
                valores = []
                for i, campo in enumerate(self.origen_campos):
                    valores.append(campo.text().strip())

                # Si el sistema de origen es UTM, agrega el valor de la zona
                if sistema_origen == "UTM":
                    zona = self.zona_origen_lineedit.text() 
                    valores.append(zona)

                resultado = self.controller.convertir(sistema_origen, sistema_destino, valores)

                # Si destino es UTM, asigna los campos correctamente
                if sistema_destino == "UTM":
                    # resultado: [Este, Norte, Zona, Letra, Altitud]
                    if resultado and len(resultado) >= 5:
                        self.destino_campos[0].setText(str(resultado[0])) 
                        self.destino_campos[1].setText(str(resultado[1]))
                        self.destino_campos[2].setText(str(resultado[4]))  
                        self.zona_destino_lineedit.setText(str(resultado[2]))  
                    elif resultado and len(resultado) >= 3:
                        self.destino_campos[0].setText(str(resultado[0]))  
                        self.destino_campos[1].setText(str(resultado[1]))  
                        self.destino_campos[2].setText("0")  
                        self.zona_destino_lineedit.setText(str(resultado[2]))
                else:
                    # Elipsoidal destino
                    if resultado:
                        for i, valor in enumerate(resultado):
                            if i < len(self.destino_campos):
                                self.destino_campos[i].setText(str(valor))

        except Exception as e:
            QMessageBox.critical(self, "Error en conversión", str(e))

        # --- LÓGICA UNIFICADA PARA MOSTRAR PUNTOS EN EL MAPA ---
        puntos_a_mostrar = []
        sistema_destino = next((r.text() for r in self.destino_radios if r.isChecked()), None)

        # Caso 1: Hay datos en la tabla de destino (conversión por lote)
        if self.tabla_destino.rowCount() > 0: # Lógica para lote desde Excel
            if sistema_destino == "Elipsoidal":
                # Columnas: Nombre, Latitud, Longitud, ...
                for i in range(self.tabla_destino.rowCount()):
                    try:
                        nombre = self.tabla_destino.item(i, 0).text()
                        lat = float(self.tabla_destino.item(i, 1).text())
                        lon = float(self.tabla_destino.item(i, 2).text())
                        puntos_a_mostrar.append((lat, lon, nombre))
                    except (ValueError, AttributeError, IndexError):
                        continue  

            elif sistema_destino == "UTM":
                # Columnas: Nombre, Este, Norte, Altitud, Zona
                for i in range(self.tabla_destino.rowCount()):
                    try:
                        nombre = self.tabla_destino.item(i, 0).text()
                        este = float(self.tabla_destino.item(i, 1).text())
                        norte = float(self.tabla_destino.item(i, 2).text())
                        zona = int(self.tabla_destino.item(i, 4).text())
                        lat, lon = este_norte_a_latlon(este, norte, zona)
                        if lat is not None and lon is not None:
                            puntos_a_mostrar.append((lat, lon, nombre))
                    except (ValueError, AttributeError, IndexError):
                        continue 
        else:
            # Caso 2: No hay datos en la tabla, fue una conversión manual.
            try:
                if sistema_destino == "Elipsoidal" and self.destino_campos[0].text() and self.destino_campos[1].text():
                    lat, lon = float(self.destino_campos[0].text()), float(self.destino_campos[1].text())
                    puntos_a_mostrar.append((lat, lon, "Punto Manual"))
                elif sistema_destino == "UTM" and self.destino_campos[0].text() and self.destino_campos[1].text() and hasattr(self, 'zona_destino_lineedit') and self.zona_destino_lineedit.text():
                    este, norte, zona = float(self.destino_campos[0].text()), float(self.destino_campos[1].text()), int(self.zona_destino_lineedit.text())
                    lat, lon = este_norte_a_latlon(este, norte, zona)
                    if lat is not None and lon is not None:
                        puntos_a_mostrar.append((lat, lon, "Punto Manual"))
            except (ValueError, IndexError, AttributeError):
                pass

        # Guardar los puntos y recargar el mapa
        self.puntos_convertidos = puntos_a_mostrar
        if self.puntos_convertidos:
            primer_punto = self.puntos_convertidos[0]
            self.cargar_mapa_base(lat=primer_punto[0], lon=primer_punto[1], zoom=12)
        else:
            self.cargar_mapa_base()

    # Limpiar los campos y tablas
    def limpiar_campos(self):
        for campo in getattr(self, "origen_campos", []):
            campo.clear()
        if hasattr(self, "zona_origen_lineedit"):
            self.zona_origen_lineedit.clear()

        for campo in getattr(self, "destino_campos", []):
            campo.clear()
        if hasattr(self, "zona_destino_lineedit"):
            self.zona_destino_lineedit.clear()

        self.tabla_origen.setRowCount(0)
        self.tabla_destino.setRowCount(0)
        self.puntos_convertidos = []
        self.cargar_mapa_base()

    #Exprtar puntos de la tabla de destino en xlsx, csv, kml o kmz
    def exportar_puntos_destino(self):
        if self.tabla_destino.rowCount() == 0:
            QMessageBox.information(self, "Exportar", "No hay puntos en la tabla de destino para exportar.")
            return

        opciones_guardado = "Archivos KML (*.kml);;Archivos KMZ (*.kmz);;Archivos CSV (*.csv);;Archivos Excel (*.xlsx)"
        archivo, filtro_seleccionado = QFileDialog.getSaveFileName(self, "Guardar archivo", "", opciones_guardado)

        if archivo:
            try:
                # Lógica para exportar a KML o KMZ
                if archivo.endswith('.kml') or archivo.endswith('.kmz'):
                    if simplekml is None:
                        QMessageBox.critical(self, "Librería Faltante", "La librería 'simplekml' es necesaria para exportar a KML/KMZ.\n\nPor favor, instálala usando: pip install simplekml")
                        return

                    kml = simplekml.Kml(name="Puntos Convertidos")
                    sistema_destino = next((r.text() for r in self.destino_radios if r.isChecked()), None)

                    for i in range(self.tabla_destino.rowCount()):
                        try:
                            nombre = self.tabla_destino.item(i, 0).text()
                            lat, lon = None, None

                            if sistema_destino == "Elipsoidal":
                                # Columnas: Nombre, Latitud, Longitud, ...
                                lat = float(self.tabla_destino.item(i, 1).text())
                                lon = float(self.tabla_destino.item(i, 2).text())
                            elif sistema_destino == "UTM":
                                # Columnas: Nombre, Este, Norte, Altitud, Zona
                                este = float(self.tabla_destino.item(i, 1).text())
                                norte = float(self.tabla_destino.item(i, 2).text())
                                zona = int(self.tabla_destino.item(i, 4).text())
                                lat, lon = este_norte_a_latlon(este, norte, zona)

                            if lat is not None and lon is not None:
                                kml.newpoint(name=nombre, coords=[(lon, lat)])

                        except (ValueError, AttributeError, IndexError, TypeError):
                            continue

                    if archivo.endswith('.kml'):
                        kml.save(archivo)
                    else:  # .kmz
                        kml.savekmz(archivo)

                # Lógica  para CSV y XLSX
                elif archivo.endswith('.csv') or archivo.endswith('.xlsx'):
                    column_headers = []
                    for j in range(self.tabla_destino.columnCount()):
                        column_headers.append(self.tabla_destino.horizontalHeaderItem(j).text())

                    df_list = []
                    for row in range(self.tabla_destino.rowCount()):
                        row_data = [self.tabla_destino.item(row, col).text() if self.tabla_destino.item(row, col) else "" for col in range(self.tabla_destino.columnCount())]
                        df_list.append(row_data)

                    df = pd.DataFrame(df_list, columns=column_headers)

                    if archivo.endswith('.csv'):
                        df.to_csv(archivo, index=False)
                    else: # .xlsx
                        df.to_excel(archivo, index=False)

                QMessageBox.information(self, "Exportación exitosa", f"Los puntos se han exportado correctamente a:\n{archivo}")
            except Exception as e:
                QMessageBox.critical(self, "Error de exportación", f"No se pudo guardar el archivo:\n{e}")

    def aplicar_estilo_moderno(self):
        self.setStyleSheet("""
            QWidget {
                background: #f0f2f5;
                font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
            }
            QGroupBox {
                border: none;
                background: transparent;
                font-weight: 600;
                color: #222b45;
                margin-top: 10px;
            }
            QLabel {
                color: #222b45;
                font-size: 12px;
                font-weight: 500;
            }
            #tableTitle {
                font-size: 14px;
                font-weight: 600;
                color: #222b45;
                margin-top: 15px;
                margin-bottom: 5px;
            }
            QLineEdit, QComboBox {
                border: 2px solid #e0e3ea;
                border-radius: 10px;
                padding: 8px 6px;
                background: #fff;
                font-size: 12px;
                color: #222b45;
                margin-bottom: 8px;
                min-width:60px;
                transition: border-color 0.2s;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3b82f6;
                background: #f5faff;
            }
            /* Estilo para el ComboBox de símbolos sobre el mapa */
            #mapSymbolComboBox {
                background: #ffffff;
                border: 1px solid #3b82f6; /* Borde temático pero más fino */
                border-radius: 16px; /* Bordes redondeados */
                padding:40px 15px; /* Espaciado equilibrado para una buena altura */
                color: #222b45;
                font-size: 12px; /* Tamaño solicitado */
                font-weight: 400; /* Normal, no negrita */
                min-width: 100px; /* Ancho adecuado */
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            #mapSymbolComboBox:hover {
                border-color: #2563eb; /* Oscurecer al pasar el mouse */
            }
            #mapSymbolComboBox::drop-down {
                border: none;
            }
            #mapSymbolComboBox QAbstractItemView {
                background: #fff;
                border: 1px solid #ccc;
                border-radius: 10px;
                selection-background-color: #3498db;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 10px;
                padding: 10px 28px;
                font-weight: 600;
                font-size: 12px;
                margin-top: 12px;
                box-shadow: 0 2px 8px rgba(59,130,246,0.08);
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QTableWidget {
                background: #fff;
                border: 2px solid #e0e3ea;
                border-radius: 10px;
                font-size: 12px;
                color: #222b45;
                gridline-color: #e0e3ea;
            }
            QHeaderView::section {
                background-color: #3b82f6;
                color: white;
                padding: 5px;
                border: none;
                font-weight: 600;
                font-size: 12px;
                border-radius: 0px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                border: none;
                background: #e0e3ea;
                width: 14px;
                margin: 0px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #3b82f6;
                min-height: 30px;
                border-radius: 7px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: none;
                border: none;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical,
            QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                background: none;
                border: none;
            }
            QRadioButton {
                color: #222b45;
                font-size: 12px;
                padding: 4px 8px;
                font-weight: 500;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #3b82f6;
                background: #fff;
            }
            QRadioButton::indicator:checked {
                background-color: #3b82f6;
                border: 2px solid #3b82f6;
            }
        """)