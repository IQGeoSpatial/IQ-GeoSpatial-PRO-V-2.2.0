
class ExpedienteModel:
    """
    Modelo de datos para un expediente.
    Mantiene el estado de la información del expediente que se está creando.
    """
    def __init__(self):
        self.nombre_expediente = ""
        self.puntos_geodesicos = []
        self.fechas_lectura = []
        self.carpeta_destino = ""
        self.incluir_video = False
        self.incluir_verificacion = False

    def is_valid(self):
        """Valida que los campos obligatorios estén completos."""
        return bool(self.nombre_expediente and self.carpeta_destino)

    def to_dict(self):
        """Serializa el modelo a un diccionario."""
        return {
            "nombre_expediente": self.nombre_expediente,
            "puntos_geodesicos": self.puntos_geodesicos,
            "fechas_lectura": self.fechas_lectura,
            "carpeta_destino": self.carpeta_destino,
            "incluir_video": self.incluir_video,
            "incluir_verificacion": self.incluir_verificacion,
        }

    @classmethod
    def from_dict(cls, data):
        """Crea una instancia del modelo a partir de un diccionario."""
        obj = cls()
        obj.nombre_expediente = data.get("nombre_expediente", "")
        obj.puntos_geodesicos = data.get("puntos_geodesicos", [])
        obj.fechas_lectura = data.get("fechas_lectura", [])
        obj.carpeta_destino = data.get("carpeta_destino", "")
        obj.incluir_video = data.get("incluir_video", False)
        obj.incluir_verificacion = data.get("incluir_verificacion", False)
        return obj