import os

class ExpedienteBuilder:
    """
    Clase responsable de construir la estructura de carpetas para un expediente.
    """
    def __init__(self, expediente, puntos, agregar_video, agregar_verif, carpeta_base, fechas_pg):
        if not expediente:
            raise ValueError("El nombre del expediente no puede estar vacío.")

        self.expediente = expediente
        self.puntos = puntos or []
        self.agregar_video = agregar_video
        self.agregar_verif = agregar_verif
        self.carpeta_base = carpeta_base
        self.fechas_pg = fechas_pg or []
        self.ruta_expediente = os.path.join(self.carpeta_base, self.expediente)

    def build(self):
        """Ejecuta la creación de toda la estructura de carpetas."""
        os.makedirs(self.ruta_expediente, exist_ok=True)
        self._crear_carpetas_principales()
        self._crear_estructura_datos_gnss()
        self._crear_estructura_fotografias()
        if self.agregar_verif:
            self._crear_estructura_verificacion()
        return self.ruta_expediente

    def _crear_carpetas_principales(self):
        """Crea las carpetas de primer nivel del expediente."""
        carpetas = [
            "1. FORMULARIOS",
            "2. DATOS GNSS",
            "3. FOTOGRAFIAS"
        ]
        if self.agregar_verif:
            carpetas.append("4. VERIFICACIÓN DE COORDENADAS")
        
        for carpeta in carpetas:
            os.makedirs(os.path.join(self.ruta_expediente, carpeta), exist_ok=True)

    def _crear_estructura_datos_gnss(self):
        """Crea la estructura dentro de DATOS GNSS."""
        ruta_datos_gnss = os.path.join(self.ruta_expediente, "2. DATOS GNSS")

        # --- DATOS ESTACIÓN BASE ---
        ruta_estacion_base = os.path.join(ruta_datos_gnss, "1. DATOS ESTACIÓN BASE")
        os.makedirs(ruta_estacion_base, exist_ok=True)

        if len(self.fechas_pg) > 1:
            # Caso con múltiples fechas
            for i, fecha in enumerate(self.fechas_pg, 1):
                ruta_fecha = os.path.join(ruta_estacion_base, f"{i}. DATOS ESTACIÓN BASE - {fecha}")
                os.makedirs(os.path.join(ruta_fecha, "1. RINEX"), exist_ok=True)
                os.makedirs(os.path.join(ruta_fecha, "2. NATIVA"), exist_ok=True)
        else:
            # Caso con una o ninguna fecha
            os.makedirs(os.path.join(ruta_estacion_base, "1. NATIVA"), exist_ok=True)
            os.makedirs(os.path.join(ruta_estacion_base, "2. RINEX"), exist_ok=True)

        # --- EFEMERIDES Y PROCESAMIENTO ---
        os.makedirs(os.path.join(ruta_datos_gnss, "2. EFEMERIDES"), exist_ok=True)
        os.makedirs(os.path.join(ruta_datos_gnss, "3. PROCESAMIENTO"), exist_ok=True)
        
        # --- Carpetas para cada punto ---
        if self.puntos:
            start_index = 4 
            for i, punto in enumerate(self.puntos, start_index):
                ruta_punto_gnss = os.path.join(ruta_datos_gnss, f"{i}. {punto}")
                os.makedirs(os.path.join(ruta_punto_gnss, "1. NATIVA"), exist_ok=True)
                os.makedirs(os.path.join(ruta_punto_gnss, "2. RINEX"), exist_ok=True)

    def _crear_estructura_fotografias(self):
        """Crea la estructura dentro de FOTOGRAFIAS."""
        ruta_fotografias = os.path.join(self.ruta_expediente, "3. FOTOGRAFIAS")
        
        subcarpetas_fotos = [
            "1. EQUIPO GNSS",
            "2. PROCESO DE MONUMENTACIÓN",
            "3. PROFUNDIDAD",
            "4. ANCLAJE DE DISCO DE BRONCE",
            "5. INCRUSTACION DEL DISCO DE BRONCE",
            "6. DISCO INSTALADO",
            "7. MEDICION DE ALTURA DE ANTENA",
            "8. FOTOGRAFIAS PANORAMICAS"
        ]
        
        if self.agregar_video:
            subcarpetas_fotos.append("9. VIDEOS")

        for sub in subcarpetas_fotos:
            os.makedirs(os.path.join(ruta_fotografias, sub), exist_ok=True)

    def _crear_estructura_verificacion(self):
        """Crea la estructura detallada dentro de VERIFICACIÓN DE COORDENADAS."""
        ruta_verificacion = os.path.join(self.ruta_expediente, "4. VERIFICACIÓN DE COORDENADAS")

        # 6. DATOS ESTACION BASE
        ruta_estacion_base_verif = os.path.join(ruta_verificacion, "6. DATOS ESTACION BASE")
        os.makedirs(os.path.join(ruta_estacion_base_verif, "1. NATIVA"), exist_ok=True)
        os.makedirs(os.path.join(ruta_estacion_base_verif, "2. RINEX"), exist_ok=True)

        # 7. DATOS GNSS
        ruta_gnss_verif = os.path.join(ruta_verificacion, "7. DATOS GNSS")
        os.makedirs(os.path.join(ruta_gnss_verif, "1. NATIVA"), exist_ok=True)
        os.makedirs(os.path.join(ruta_gnss_verif, "2. PROCESAMIENTO"), exist_ok=True)
        os.makedirs(os.path.join(ruta_gnss_verif, "3. RINEX"), exist_ok=True)

        # Resto de carpetas
        otras_carpetas = [
            "8. FICHAS ERP",
            "9. EFEMERIDES EMPLEADAS",
            "10. FOTOS RECEPTOR GNSS",
            "11. FOTOS ALTURA DE ANTENA",
            "12. FOTOS PANORAMICAS",
            "13. RECIBOS DE INGRESO",
            "14. RESULTADOS VALIDACION"
        ]
        for carpeta in otras_carpetas:
            os.makedirs(os.path.join(ruta_verificacion, carpeta), exist_ok=True)