import pyproj

def este_norte_a_latlon(este, norte, zona, hemisferio_sur=True):
    """
    Convierte coordenadas UTM (Este, Norte) a Latitud/Longitud.
    """
    try:
        # Validar que la zona esté entre 1 y 60
        if not (1 <= zona <= 60):
            raise ValueError(f"Zona UTM inválida: {zona}. Debe estar entre 1 y 60.")

        # Define el sistema de coordenadas UTM
        proj_utm = pyproj.CRS(f"+proj=utm +zone={zona} +south={hemisferio_sur} +ellps=WGS84")

        # Define el sistema de coordenadas geográficas (Lat/Lon)
        proj_latlon = pyproj.CRS("EPSG:4326")

        # Crear el transformador
        transformer = pyproj.Transformer.from_crs(proj_utm, proj_latlon, always_xy=True)

        # Realiza la transformación
        lon, lat = transformer.transform(este, norte)

        return lat, lon
    except Exception as e:
        print(f"Error en la conversión de coordenadas: {e}")
        return None, None