#Here are the contents for the file `src/main.py`:

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from PyQt5.QtWidgets import QApplication
from GUI.dashboard_gui import DashboardApp
from GUI.splash import SplashScreen
from GUI.themes import LIGHT_THEME
from utils.resource_path import resource_path

import os
import tempfile
import time

def limpiar_temp(dias=1):
    """Limpia archivos temporales creados por esta aplicación que son más antiguos que 'dias'."""
    temp_dir = tempfile.gettempdir() 
    ahora = time.time()
    # Prefijos de archivos temporales usados por la aplicación
    prefijos_app = ("iq_", "recorte_", "mapa_temp")
    for nombre in os.listdir(temp_dir):
        if nombre.startswith(prefijos_app):
            ruta = os.path.join(temp_dir, nombre)
            try:
                # Comprobar si es un archivo y si es más antiguo que el límite
                if os.path.isfile(ruta) and (ahora - os.path.getmtime(ruta) > dias * 86400):
                    os.remove(ruta)
                # Opcional: limpiar también directorios temporales vacíos o antiguos
                elif os.path.isdir(ruta):
                    # Aquí se podría añadir lógica para limpiar directorios si es necesario
                    pass
            except Exception:
                # Ignorar errores si el archivo está en uso, etc.
                pass

# Llama a esta función al inicio
limpiar_temp(dias=1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Aplicar tema claro por defecto, reemplazando el placeholder de la imagen
    bg_image_path = resource_path(os.path.join("Assets", "Image", "license_bg.jpg")).replace(os.sep, '/')
    app.setStyleSheet(LIGHT_THEME.replace("{bg_image_path}", bg_image_path))
    
    splash = SplashScreen()
    splash.show()
    # Forzar a Qt a procesar eventos para que la splash screen se dibuje inmediatamente
    app.processEvents()

    # Ahora, con la splash screen visible, creamos la ventana principal (la parte lenta)
    main_window = DashboardApp()

    # El callback que se ejecutará cuando la animación de la splash screen termine
    def show_main():
        main_window.show()

    splash.start(show_main) # Inicia la animación y asigna el callback
    sys.exit(app.exec_())

# Python -m PyInstaller --noconfirm --onefile --windowed --icon=Assets\Icono\icono.ico --add-data "Assets;Assets" main.py
#para poner instalador
# pyinstaller --noconfirm --windowed --icon=Assets\Icono\icono.ico --add-data "Assets;Assets" main.py