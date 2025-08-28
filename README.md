# IQ GeoSpatial PRO V2.0

Aplicación de escritorio para la certificación de puntos geodésicos, gestión de imágenes, descarga de efemérides y conversión de documentos Word a PDF.

## Características principales
- Importación de datos desde Excel.
- Gestión y visualización de imágenes asociadas a puntos geodésicos.
- Descarga automática de efemérides GNSS desde servidores internacionales.
- Conversión masiva de documentos Word a PDF con generación de miniaturas.
- Interfaz moderna y responsiva con PyQt5.

## Instalación
1. Clona este repositorio o copia los archivos a tu equipo.
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:

```bash
python main.py
```

## Empaquetado (opcional)
Para crear un ejecutable con PyInstaller:

```bash
pyinstaller --noconfirm --windowed --icon=Assets\Icono\icono.ico --add-data "Assets;Assets" main.py
```

## Estructura del proyecto
- `main.py`: Lanzador principal de la aplicación.
- `GUI/`: Interfaces gráficas (ventanas, diálogos, widgets).
- `Controllers/`: Lógica de control y conexión entre UI y servicios.
- `Models/`: Modelos de datos y base de datos.
- `Services/`: Servicios de conversión, miniaturas, etc.
- `utils/`: Utilidades y funciones auxiliares.
- `Assets/`: Imágenes, iconos y plantillas.

## Requisitos
- Windows 10/11 (recomendado)
- Python 3.10 o superior
- Microsoft Word instalado (para la conversión de .docx a PDF)

## Créditos
Desarrollado por IQ GeoSpatial

Contacto: iqgeospatial@gmail.com