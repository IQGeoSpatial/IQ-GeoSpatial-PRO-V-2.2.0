# from PyQt5.QtWidgets import QApplication, QMessageBox
# from PyQt5.QtCore import QUrl
# from PyQt5.QtGui import QDesktopServices
# from GUI.expediente_gui import ExpedienteApp, DialogoFormularios, QDialog
# from GUI.efemerides_dialog import EfemeridesDialog
# from GUI.pdf_converter_dialog import PdfConverterDialog
# from Controllers.expediente_controller import ExpedienteController
# # from Models.DataBase import CodigoDB
# from Models.Expediente_models import ExpedienteModel
# from GUI.themes import LIGHT_THEME, DARK_THEME
# from utils.resource_path import resource_path
# import os

# class DashboardController:
#     def __init__(self, view):
#         self.view = view
#         self.expediente_window = None
#         self.formularios_window = None
#         self.efemerides_window = None
#         self.licencia_window = None
#         self.pdf_converter_window = None
#         self.is_dark_theme = False

#     def mostrar_expediente(self):
#         """Abre la ventana principal de gestión de expedientes."""
#         if self.expediente_window is None or not self.expediente_window.isVisible():
#             self.expediente_window = ExpedienteApp()
#             self.expediente_window.show()
#         else:
#             self.expediente_window.activateWindow()

#     def mostrar_formularios(self):
#         """Abre el diálogo para generar formularios."""
#         if self.formularios_window is None or not self.formularios_window.isVisible():
#             temp_model = ExpedienteModel()
#             # temp_db = CodigoDB()
#             temp_controller = ExpedienteController(temp_model, self.view)
#             self.formularios_window = DialogoFormularios(temp_controller, self.view)
#             self.formularios_window.show()
#         else:
#             self.formularios_window.activateWindow()

#     def mostrar_efemerides(self):
#         """Abre el diálogo para descargar efemérides."""
#         if self.efemerides_window is None or not self.efemerides_window.isVisible():
#             self.efemerides_window = EfemeridesDialog(self.view)
#             self.efemerides_window.show()
#         else:
#             self.efemerides_window.activateWindow()

#     def mostrar_pdf_converter(self):
#         """Abre el diálogo para convertir archivos a PDF."""
#         if self.pdf_converter_window is None or not self.pdf_converter_window.isVisible():
#             self.pdf_converter_window = PdfConverterDialog(self.view)
#             self.pdf_converter_window.show()
#         else:
#             self.pdf_converter_window.activateWindow()

#     def mostrar_video(self):
#         """Abre el video tutorial en el navegador web predeterminado del usuario."""
#         # --- ¡IMPORTANTE! ---
#         youtube_video_id = "_prhwIH19Mc" # <-- USA TU ID DE VIDEO REAL
        
#         video_url = f"https://www.youtube.com/watch?v={youtube_video_id}"
        
#         QDesktopServices.openUrl(QUrl(video_url))

#     def toggle_theme(self):
#         """Cambia entre el tema claro y oscuro para toda la aplicación."""
#         app = QApplication.instance()
#         bg_image_path = resource_path(os.path.join("Assets", "Image", "license_bg.jpg")).replace(os.sep, '/')

#         if self.is_dark_theme:
#             # Aplicar tema claro
#             light_stylesheet = LIGHT_THEME.replace("{bg_image_path}", bg_image_path)
#             app.setStyleSheet(light_stylesheet)
#             self.view.theme_btn.setText("🌙") 
#         else:
#             # Aplicar tema oscuro
#             dark_stylesheet = DARK_THEME.replace("{bg_image_path}", bg_image_path)
#             app.setStyleSheet(dark_stylesheet)
#             self.view.theme_btn.setText("☀️") 
#         self.is_dark_theme = not self.is_dark_theme

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from GUI.expediente_gui import ExpedienteApp, DialogoFormularios, QDialog
from GUI.efemerides_dialog import EfemeridesDialog
from GUI.pdf_converter_dialog import PdfConverterDialog
from GUI.licencia_dialog import LicenciaDialog
from Controllers.expediente_controller import ExpedienteController
from Models.DataBase import CodigoDB
from Models.Expediente_models import ExpedienteModel
from GUI.themes import LIGHT_THEME, DARK_THEME
from utils.resource_path import resource_path
# from utils.licencia_utils import puede_usar_app, registrar_uso
import os

class DashboardController:
    def __init__(self, view):
        self.view = view
        self.expediente_window = None
        self.formularios_window = None
        self.efemerides_window = None
        self.licencia_window = None
        self.pdf_converter_window = None
        self.is_dark_theme = False

    def mostrar_expediente(self):
        """Abre la ventana principal de gestión de expedientes."""
        if self.expediente_window is None or not self.expediente_window.isVisible():
            self.expediente_window = ExpedienteApp()
            self.expediente_window.show()
        else:
            self.expediente_window.activateWindow()

    def mostrar_formularios(self):
        """Abre el diálogo para generar formularios."""
        if self.formularios_window is None or not self.formularios_window.isVisible():
                # Creamos una instancia temporal de ExpedienteController para el diálogo
            temp_model = ExpedienteModel()
            temp_db = CodigoDB()
            temp_controller = ExpedienteController(temp_model, self.view, temp_db)
            self.formularios_window = DialogoFormularios(temp_controller, self.view)
            self.formularios_window.show()
        else:
            self.formularios_window.activateWindow()

    def mostrar_efemerides(self):
        """Abre el diálogo para descargar efemérides."""
        if self.efemerides_window is None or not self.efemerides_window.isVisible():
            self.efemerides_window = EfemeridesDialog(self.view)
            self.efemerides_window.show()
        else:
            self.efemerides_window.activateWindow()

    def mostrar_pdf_converter(self):
        """Abre el diálogo para convertir archivos a PDF."""
        # def abrir_ventana():
        if self.pdf_converter_window is None or not self.pdf_converter_window.isVisible():
            self.pdf_converter_window = PdfConverterDialog(self.view)
            self.pdf_converter_window.show()
        else:
            self.pdf_converter_window.activateWindow()
        # self._ejecutar_con_licencia(abrir_ventana)

    def mostrar_video(self):
        """Abre el video tutorial en el navegador web predeterminado del usuario."""
        # --- ¡IMPORTANTE! ---
        youtube_video_id = "AZY0F_B5gw0" # <-- USA TU ID DE VIDEO REAL
        
        video_url = f"https://www.youtube.com/watch?v={youtube_video_id}"
        
        QDesktopServices.openUrl(QUrl(video_url))

    def toggle_theme(self):
        """Cambia entre el tema claro y oscuro para toda la aplicación."""
        app = QApplication.instance()
        bg_image_path = resource_path(os.path.join("Assets", "Image", "license_bg.jpg")).replace(os.sep, '/')

        if self.is_dark_theme:
            # Aplicar tema claro
            light_stylesheet = LIGHT_THEME.replace("{bg_image_path}", bg_image_path)
            app.setStyleSheet(light_stylesheet)
            self.view.theme_btn.setText("🌙") # Cambia a icono de luna
        else:
            # Aplicar tema oscuro
            dark_stylesheet = DARK_THEME.replace("{bg_image_path}", bg_image_path)
            app.setStyleSheet(dark_stylesheet)
            self.view.theme_btn.setText("☀️") # Cambia a icono de sol
        self.is_dark_theme = not self.is_dark_theme