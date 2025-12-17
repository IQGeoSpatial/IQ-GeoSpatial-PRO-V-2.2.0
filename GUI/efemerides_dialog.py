import paramiko
import os
import ftplib
import paramiko

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QRadioButton,
    QCalendarWidget, QGroupBox, QTextEdit, QFileDialog, QMessageBox,
    QProgressBar, QWidget, QGridLayout
)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPainter, QPixmap, QTransform
from utils.resource_path import resource_path
from utils.efemeride import date_to_gps_week, date_to_julian_day, FTP_CONFIG, EPHEM_TYPE_CONFIG

class FtpWorker(QThread):
    """
    Subproceso de trabajo para manejar el proceso de descarga FTP sin congelar la GUI.
    """
    log_message = pyqtSignal(str)
    progress_update = pyqtSignal(int)
    download_finished = pyqtSignal(bool, str)

    def __init__(self, selected_date, save_path, product_type, source):
        super().__init__()
        self.selected_date = selected_date
        self.save_path = save_path
        self.product_type = product_type
        self.source = source

    def run(self):
        """
        Se conecta al servidor FTP de la ESA y descarga el archivo de efemérides de transmisión diaria.
        """
        try:
            config = FTP_CONFIG.get(self.source)
            ephem_config = EPHEM_TYPE_CONFIG.get(self.product_type)

            if not config or not ephem_config:
                raise ValueError(f"Configuración no válida para {self.source} - {self.product_type}")

            # --- SFTP (paramiko) ---
            host = "gssc.esa.int"
            port = 2200
            username = "anonymous"
            password = ""
            interval = config["interval"]
            ephem_code = ephem_config["code"]
            duration = ephem_config["duration"]
            year = self.selected_date.year
            doy = self.selected_date.timetuple().tm_yday
            gps_week, _ = date_to_gps_week(self.selected_date)
            filename = f"{self.source}0OPS{ephem_code}_{year}{doy:03d}0000_{duration}_{interval}_ORB.SP3.gz"
            remote_dir = f"/gnss/products/{gps_week}"
            local_filepath = os.path.join(self.save_path, filename)
            self.log_message.emit(f"[SFTP] Conectando a {host}:{port} ...")
            self.progress_update.emit(10)
            try:
                transport = paramiko.Transport((host, port))
                transport.connect(username=username, password=password)
                sftp = paramiko.SFTPClient.from_transport(transport)
                self.log_message.emit(f"[SFTP] Conectado. Listando archivos en {remote_dir} ...")
                files = sftp.listdir(remote_dir)
                self.log_message.emit(f"[SFTP] Archivos en {remote_dir}: {files}")
                if filename not in files:
                    self.log_message.emit(f"[SFTP][ERROR] El archivo '{filename}' NO está en la lista del servidor. Revisa mayúsculas/minúsculas y espacios.")
                    sftp.close()
                    transport.close()
                    self.download_finished.emit(False, f"El archivo '{filename}' no está en el servidor de la ESA.")
                    return
                self.log_message.emit(f"[SFTP] Descargando archivo: {filename}")
                with open(local_filepath, 'wb') as f:
                    sftp.getfo(f"{remote_dir}/{filename}", f)
                sftp.close()
                transport.close()
                self.progress_update.emit(100)
                self.log_message.emit(f"\n¡Descarga SFTP completada!\nArchivo guardado en: {local_filepath}")
                self.download_finished.emit(True, local_filepath)
            except Exception as e:
                self.log_message.emit(f"[SFTP][ERROR] {e}")
                self.download_finished.emit(False, str(e))
                return

        except ftplib.error_perm as e:
            error_msg = f"Error: No se encontró el archivo o directorio en el servidor. Es posible que no haya datos para la fecha seleccionada.\n\nDetalle: {e}"
            self.log_message.emit(error_msg)
            self.download_finished.emit(False, error_msg)
        except Exception as e:
            error_msg = f"Ocurrió un error inesperado: {e}"
            self.log_message.emit(error_msg)
            self.download_finished.emit(False, error_msg)
        finally:
            self.progress_update.emit(0)

class AnimatedImageWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(image_path)
        self.setMinimumSize(150, 150)
        self.setMaximumSize(150, 150)

        self._angle = 0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(30) # ~33 FPS

    def _animate(self):
        self._angle = (self._angle + 1) % 360
        self.update()

    def paintEvent(self, event):
        if self.pixmap.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Escalar la imagen base al tamaño deseado
        scaled_pixmap = self.pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Crear una transformación y rotarla
        transform = QTransform().rotate(self._angle)
        rotated_pixmap = scaled_pixmap.transformed(transform, Qt.SmoothTransformation)

        # Centrar la imagen rotada en el widget
        x = (self.width() - rotated_pixmap.width()) / 2
        y = (self.height() - rotated_pixmap.height()) / 2

        painter.drawPixmap(int(x), int(y), rotated_pixmap)
        painter.end()

class EfemeridesDialog(QDialog):
    def list_sftp_files(self):
        """Lista todos los archivos en la carpeta 2368 usando SFTP y los muestra en el log."""
        host = "gssc.esa.int"
        port = 2200
        username = "anonymous"
        password = ""
        remote_dir = "/gnss/products/2368"
        try:
            self.update_log(f"[SFTP] Conectando a {host}:{port} ...")
            transport = paramiko.Transport((host, port))
            transport.connect(username=username, password=password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            self.update_log(f"[SFTP] Conectado. Listando archivos en {remote_dir} ...")
            files = sftp.listdir(remote_dir)
            self.update_log(f"[SFTP] Archivos en {remote_dir}:")
            for f in files:
                self.update_log(f"    {f}")
            sftp.close()
            transport.close()
        except Exception as e:
            self.update_log(f"[SFTP][ERROR] {e}")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.setWindowTitle("Descargar Efemérides")
        self.setObjectName("EfemeridesDialog")
        logo_path = resource_path(os.path.join("Assets", "Image", "efemeride.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))
        else:
            pass
        self.setMinimumSize(800, 500)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Left Panel (Calendar) ---
        self.calendar = QCalendarWidget()
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setSelectedDate(QDate.currentDate())
        main_layout.addWidget(self.calendar, 1)

        # --- Right Panel (Controls) ---
        right_panel = QWidget()
        right_panel.setObjectName("RightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        # Title
        title_label = QLabel("Descarga de Efemérides GNSS")
        title_label.setObjectName("Titulo") # Usa el estilo de los temas
        title_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(title_label)

        # Source Group
        source_group = QGroupBox("Fuente")
        source_layout = QGridLayout(source_group)
        self.rb_cod = QRadioButton("COD")
        self.rb_esa = QRadioButton("ESA")
        self.rb_igs = QRadioButton("IGS")
        self.rb_gfz = QRadioButton("GFZ")
        self.rb_whu = QRadioButton("WHU")
        self.rb_esa.setChecked(True) # ESA por defecto
        source_layout.addWidget(self.rb_cod, 0, 0)
        source_layout.addWidget(self.rb_esa, 0, 1)
        source_layout.addWidget(self.rb_igs, 0, 2)
        source_layout.addWidget(self.rb_gfz, 1, 0)
        source_layout.addWidget(self.rb_whu, 1, 1)
        right_layout.addWidget(source_group)
        # Ephemeris Type Group
        ephem_type_group = QGroupBox("Tipo de Efeméride")
        ephem_type_layout = QHBoxLayout(ephem_type_group)
        self.rb_ultrarapid = QRadioButton("Ultra-rápido")
        self.rb_rapid = QRadioButton("Rápido")
        self.rb_final = QRadioButton("Final")
        self.rb_rapid.setChecked(True) # Rápido por defecto
        ephem_type_layout.addWidget(self.rb_ultrarapid)
        ephem_type_layout.addWidget(self.rb_rapid)
        ephem_type_layout.addWidget(self.rb_final)
        right_layout.addWidget(ephem_type_group)

        # Información de Fecha (Julian Day centrado, segunda fila Day of Year y GPS Week, tercera fila GPS Week Number centrado)
        font_bold = self.font()
        font_bold.setBold(True)
        fecha_grid = QGridLayout()
        fecha_grid.setHorizontalSpacing(30)
        fecha_grid.setVerticalSpacing(10)

        self.lbl_julian_title = QLabel("Julian Day Number:")
        self.lbl_julian_title.setFont(font_bold)
        self.lbl_julian_day = QLabel("...")
        self.lbl_julian_day.setAlignment(Qt.AlignCenter)

        self.lbl_doy_title = QLabel("Day of Year:")
        self.lbl_doy_title.setFont(font_bold)
        self.lbl_doy_title.setAlignment(Qt.AlignRight)
        self.lbl_doy = QLabel("...")
        self.lbl_doy.setAlignment(Qt.AlignCenter)
        self.lbl_gps_week_title = QLabel("GPS Week:")
        self.lbl_gps_week_title.setFont(font_bold)
        self.lbl_gps_week_title.setAlignment(Qt.AlignCenter)
        self.lbl_gps_week = QLabel("...")
        self.lbl_gps_week.setAlignment(Qt.AlignCenter)

        self.lbl_gps_week_num_title = QLabel("GPS Week Number:")
        self.lbl_gps_week_num_title.setFont(font_bold)
        self.lbl_gps_week_num = QLabel("...")
        self.lbl_gps_week_num.setAlignment(Qt.AlignCenter)

        # Primera fila: Julian Day Number centrado en las 4 columnas
        fecha_grid.addWidget(self.lbl_julian_title, 0, 1, alignment=Qt.AlignRight)
        fecha_grid.addWidget(self.lbl_julian_day, 0, 2, alignment=Qt.AlignLeft)
        fecha_grid.setColumnStretch(0, 1)
        fecha_grid.setColumnStretch(3, 1)

        # Segunda fila: Day of Year y GPS Week (toda la fila centrada)
        # Usar una sola celda que abarque todas las columnas y un layout horizontal centrado
        fila2_widget = QWidget()
        fila2_layout = QHBoxLayout(fila2_widget)
        fila2_layout.setContentsMargins(0, 0, 0, 0)
        fila2_layout.setSpacing(30)
        fila2_layout.setAlignment(Qt.AlignCenter)
        fila2_layout.addWidget(self.lbl_doy_title)
        fila2_layout.addWidget(self.lbl_doy)
        fila2_layout.addSpacing(40)
        fila2_layout.addWidget(self.lbl_gps_week_title)
        fila2_layout.addWidget(self.lbl_gps_week)
        fecha_grid.addWidget(fila2_widget, 1, 0, 1, 5, alignment=Qt.AlignCenter)

        # Tercera fila: GPS Week Number centrado en las 4 columnas
        fecha_grid.addWidget(self.lbl_gps_week_num_title, 2, 1, alignment=Qt.AlignRight)
        fecha_grid.addWidget(self.lbl_gps_week_num, 2, 2, alignment=Qt.AlignLeft)

        right_layout.addLayout(fecha_grid)

        # --- Imagen animada ---
        efemeride_img_path = resource_path(os.path.join("Assets", "Image", "efemeride.png"))
        self.animated_image = AnimatedImageWidget(efemeride_img_path)
        image_container = QWidget()
        image_layout = QHBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(self.animated_image)
        right_layout.addWidget(image_container)

        right_layout.addStretch()

        # Download Button
        self.download_btn = QPushButton("Descargar Efemérides")
        self.download_btn.setCursor(Qt.PointingHandCursor)
        right_layout.addWidget(self.download_btn)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        right_layout.addWidget(self.progress_bar)

        main_layout.addWidget(right_panel, 1)
        self.update_date_info() # Cargar datos para la fecha actual al iniciar

    def connect_signals(self):
        self.download_btn.clicked.connect(self.start_download)
        self.calendar.selectionChanged.connect(self.update_date_info)


    def start_download(self):
        self.progress_bar.setValue(0)

        save_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Destino", os.path.expanduser("~\\Desktop"))
        if not save_path:
            return

        # Determinar la fuente seleccionada
        if self.rb_cod.isChecked():
            source = "COD"
        elif self.rb_esa.isChecked():
            source = "ESA"
        elif self.rb_igs.isChecked():
            source = "IGS"
        elif self.rb_gfz.isChecked():
            source = "GFZ"
        elif self.rb_whu.isChecked():
            source = "WHU"
        else:
            source = "ESA" # Fallback

        # Determinar el tipo de efeméride seleccionado
        if self.rb_ultrarapid.isChecked():
            ephem_type = "Ultra-rápido"
        elif self.rb_rapid.isChecked():
            ephem_type = "Rápido"
        elif self.rb_final.isChecked():
            ephem_type = "Final"
        else:
            ephem_type = "Rápido" # Fallback

        selected_date = self.calendar.selectedDate().toPyDate()

        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.show_status_message("Descargando efemérides... Por favor espere.")
        # Start the FTP worker thread
        self.worker = FtpWorker(selected_date, save_path, ephem_type, source)
        self.worker.progress_update.connect(self.update_progress)
        self.worker.download_finished.connect(self.download_finished)
        self.worker.log_message.connect(self.show_status_message)
        self.worker.start()

    def show_status_message(self, message):
        self.progress_bar.setTextVisible(False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_date_info(self):
        """Calcula y muestra la información de la fecha seleccionada."""
        selected_qdate = self.calendar.selectedDate()
        selected_date = selected_qdate.toPyDate()

        # Day of Year
        doy = selected_date.timetuple().tm_yday
        self.lbl_doy.setText(str(doy))

        # GPS Week
        gps_week, day_of_week = date_to_gps_week(selected_date)
        self.lbl_gps_week.setText(str(gps_week))

        # GPS Week Number
        self.lbl_gps_week_num.setText(f"{gps_week}{day_of_week}")

        # Julian Day
        julian_day = date_to_julian_day(selected_date)
        self.lbl_julian_day.setText(str(julian_day))

    def download_finished(self, success, message):
        self.download_btn.setEnabled(True)
        self.progress_bar.setTextVisible(False)
        if success:
            self.show_status_message("Descarga completada.")
            QMessageBox.information(self, "Descarga Completa", f"El archivo se ha descargado correctamente en:\n{message}")
        else:
            self.show_status_message("Error o efeméride no disponible.")
            # Mensaje informativo sobre la disponibilidad de efemérides
            info = (
                "<b>Disponibilidad de Efemérides:</b><br>"
                "<b>Ultra-rápidas (IGU):</b> Cada 6 horas (00:00, 06:00, 12:00, 18:00 UTC)<br>"
                "<b>Rápida:</b> Al día siguiente (tarde) — Buen equilibrio velocidad/precisión<br>"
                "<b>Final:</b> 10 a 15 días después — Máxima precisión (científica)<br><br>"
                f"<b>Motivo:</b> {message}"
            )
            QMessageBox.warning(self, "Efeméride no disponible", info)

    def closeEvent(self, event):
        """
        Ensure the worker thread is terminated if the dialog is closed during download.
        """
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        super().closeEvent(event)