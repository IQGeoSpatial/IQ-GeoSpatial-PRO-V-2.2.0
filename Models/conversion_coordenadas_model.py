import utm
from utils.map_utils import este_norte_a_latlon

def convertir(sistema_origen, sistema_destino, valores):
    if sistema_origen == "Elipsoidal" and sistema_destino == "UTM":
        try:
            lat = float(valores[0])
            lon = float(valores[1])
            altura = valores[2] if len(valores) > 2 else ""
            este, norte, zona, letra = utm.from_latlon(lat, lon)
            return [str(este), str(norte), str(zona), str(letra), str(altura)]
        except Exception as e:
            # Retorna una lista con mensaje de error en cada campo esperado
            return [f"Error: {e}", "", "", "", ""]
    elif sistema_origen == "UTM" and sistema_destino == "Elipsoidal":
        try:
            este = float(valores[0])
            norte = float(valores[1])
            zona = int(valores[3])
            hemisferio_sur = True  # Ajusta según tu lógica
            lat, lon = este_norte_a_latlon(este, norte, zona, hemisferio_sur)
            altura = valores[2] if len(valores) > 3 else ""
            # Si la conversión falla, lat/lon serán None

            if lat is None or lon is None:
                return ["Error: conversión fallida", "", ""]
            return [str(lat), str(lon), str(altura)]
        except Exception as e:
            return [f"Error: {e}", "", ""]
    elif sistema_origen == sistema_destino:
        return ["Las coordenadas ya están en el sistema destino.", *valores]
    else:
        return ["Conversión no implementada o no posible."]