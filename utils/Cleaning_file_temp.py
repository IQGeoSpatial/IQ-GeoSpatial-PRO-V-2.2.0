import os
import tempfile
import glob

def limpiar_archivos_temporales_mejorado():
    """
    Busca y elimina archivos temporales específicos de la aplicación
    y además reporta carpetas sospechosas de gran tamaño.
    """
    temp_dir = tempfile.gettempdir()
    print(f"Buscando archivos temporales en: {temp_dir}\n")

    # Patrones actualizados para incluir más posibilidades
    patrones_a_buscar = [
        "recorte_*.png",          # Capturas de imagen del formulario.
        "mapa_temp.html",         # Mapa de ubicación de puntos.
        "thumb_*.png",            # Posibles miniaturas del convertidor PDF.
        "preview_*.png",          # Otro posible nombre para miniaturas.
        "word_preview_*.png"      # Otro posible nombre para miniaturas.
    ]

    archivos_eliminados_count = 0
    espacio_liberado_bytes = 0

    # --- Parte 1: Eliminar archivos conocidos ---
    print("--- Eliminando archivos temporales conocidos ---")
    for patron in patrones_a_buscar:
        patron_completo = os.path.join(temp_dir, patron)
        archivos_encontrados = glob.glob(patron_completo)

        if not archivos_encontrados:
            continue

        for archivo_a_eliminar in archivos_encontrados:
            try:
                tamaño_archivo = os.path.getsize(archivo_a_eliminar)
                os.remove(archivo_a_eliminar)
                archivos_eliminados_count += 1
                espacio_liberado_bytes += tamaño_archivo
            except OSError:
                continue # Ignorar si no se puede eliminar

    print("\n\n================ RESUMEN DE LA LIMPIEZA DE ARCHIVOS ================")
    if archivos_eliminados_count > 0:
        if espacio_liberado_bytes >= 1024**3:
            espacio_legible = f"{espacio_liberado_bytes / 1024**3:.2f} GB"
        elif espacio_liberado_bytes >= 1024**2:
            espacio_legible = f"{espacio_liberado_bytes / 1024**2:.2f} MB"
        else:
            espacio_legible = f"{espacio_liberado_bytes / 1024:.2f} KB"
        
        print(f"Se eliminaron un total de {archivos_eliminados_count} archivos.")
        print(f"Espacio liberado: {espacio_legible}")
    else:
        print("No se encontraron archivos temporales conocidos para limpiar.")
    print("====================================================================\n")


    # --- Parte 2: Analizar carpetas grandes (posibles extracciones de ZIP) ---
    print("--- Analizando carpetas grandes (posibles extracciones ZIP sin borrar) ---")
    print("AVISO: Este script no borrará carpetas, solo te informará de las sospechosas.")
    
    carpetas_grandes_encontradas = 0
    try:
        for entry in os.scandir(temp_dir):
            if entry.is_dir():
                try:
                    # Calcula el tamaño total de la carpeta de forma recursiva
                    dir_size_bytes = 0
                    for dirpath, _, filenames in os.walk(entry.path):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            if not os.path.islink(fp):
                                dir_size_bytes += os.path.getsize(fp)
                    
                    # Reportar si la carpeta es mayor a 100 MB
                    if dir_size_bytes > 100 * 1024 * 1024:
                        print(f"-> ¡SOSPECHOSO! Carpeta grande encontrada: '{entry.name}' ({dir_size_bytes / 1024**2:.1f} MB)")
                        print(f"   Ruta: {entry.path}")
                        print(f"   Revisa esta carpeta manualmente y bórrala si contiene archivos de tu programa.")
                        carpetas_grandes_encontradas += 1

                except (OSError, PermissionError):
                    continue # Ignorar carpetas a las que no tenemos acceso
    except Exception as e:
        print(f"No se pudo analizar los subdirectorios: {e}")

    if carpetas_grandes_encontradas == 0:
        print("No se encontraron carpetas sospechosamente grandes.")


# Esta parte asegura que el código se ejecute cuando corras el script
if __name__ == "__main__":
    limpiar_archivos_temporales_mejorado()
    # Esta línea final hace una pausa para que puedas leer el resultado
    input("\nAnálisis finalizado. Presiona Enter para salir...")

