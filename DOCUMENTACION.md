# IQ GeoSpatial-PRO

Aplicación de escritorio desarrollada en Python y PyQt5 para el procesamiento y visualización de datos geoespaciales.

## Características Principales

- **Interfaz Gráfica de Usuario (GUI)**: Construida con PyQt5 para una experiencia de usuario fluida.
- **Pantalla de Bienvenida (Splash Screen)**: Muestra una pantalla de carga animada mientras la aplicación principal se inicializa.
- **Gestión de Temas**: Soporte para temas visuales (ej. tema claro) para personalizar la apariencia.
- **Limpieza Automática**: Limpia archivos temporales antiguos generados por la aplicación para mantener el sistema ordenado.
- **Empaquetado Sencillo**: Se puede compilar en un único archivo ejecutable (`.exe`) utilizando PyInstaller para una fácil distribución.

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera para mantener el código limpio y modular.

```
.
├── main.py               # Punto de entrada principal de la aplicación
├── requirements.txt      # Lista de dependencias de Python
├── Assets/                 # Recursos estáticos como imágenes e iconos
│   ├── Icono/
│   │   └── icono.ico
│   └── Image/
│       └── license_bg.jpg
├── GUI/                    # Módulos relacionados con la Interfaz Gráfica
│   ├── __init__.py
│   ├── dashboard_gui.py  # Ventana principal de la aplicación
│   ├── splash.py         # Lógica de la pantalla de bienvenida
│   └── themes.py         # Hojas de estilo (QSS) para los temas
└── utils/                  # Funciones de utilidad reutilizables
    ├── __init__.py
    └── resource_path.py  # Función para resolver rutas de assets en PyInstaller
```

## Instalación y Configuración (Desde el código fuente)

Para ejecutar la aplicación desde el código fuente, sigue estos pasos:

1.  **Clonar el Repositorio** (si está en un control de versiones como Git)
    ```bash
    git clone <url-del-repositorio>
    cd IQ-GeoSpatial-PRO-V-2.1.0
    ```

2.  **Crear un Entorno Virtual**
    Es una buena práctica aislar las dependencias del proyecto.
    ```bash
    python -m venv venv
    ```

3.  **Activar el Entorno Virtual**
    - En Windows:
      ```bash
      .\venv\Scripts\activate
      ```
    - En macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

4.  **Instalar las Dependencias**
    Instala todas las librerías necesarias listadas en `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## Uso

Una vez que el entorno está configurado y las dependencias instaladas, puedes ejecutar la aplicación con el siguiente comando:

```bash
python main.py
```

## Compilación del Ejecutable

Para crear un archivo `.exe` único que no requiera que el usuario final tenga Python instalado, puedes usar PyInstaller.

Ejecuta el siguiente comando desde la raíz del proyecto:

```bash
pyinstaller --noconfirm --onefile --windowed --icon=Assets\Icono\icono.ico --add-data "Assets;Assets" main.py
```

**Explicación de los flags:**

-   `--noconfirm`: No pedir confirmación para sobrescribir archivos.
-   `--onefile`: Empaqueta todo en un único archivo ejecutable.
-   `--windowed`: Evita que se abra una consola de comandos al ejecutar la aplicación.
-   `--icon`: Especifica el icono de la aplicación.
-   `--add-data "Assets;Assets"`: Incluye el directorio `Assets` completo dentro del ejecutable, asegurando que las imágenes e iconos estén disponibles.

El ejecutable se encontrará en la carpeta `dist/` que se creará en el directorio del proyecto.

## Documentación del Código

### `main.py`
Es el corazón de la aplicación. Sus responsabilidades son:
-   **Configuración de `sys.path`**: Asegura que los módulos locales (`GUI`, `utils`) se puedan importar correctamente tanto en modo de desarrollo como en el ejecutable de PyInstaller.
-   **Limpieza de Temporales**: Ejecuta la función `limpiar_temp()` al inicio para eliminar archivos residuales de sesiones anteriores.
-   **Inicialización de `QApplication`**: Crea la instancia de la aplicación Qt.
-   **Aplicación de Tema**: Carga y aplica la hoja de estilos (QSS) para el tema visual.
-   **Gestión del Splash Screen**: Muestra la pantalla de bienvenida, carga la ventana principal en segundo plano y luego muestra la ventana principal cuando la animación del splash termina.

### `GUI/`
Este paquete contiene todos los componentes de la interfaz de usuario.

### `utils/`
Este paquete contiene funciones de ayuda como `resource_path.py`, que es crucial para que PyInstaller encuentre los `Assets`.