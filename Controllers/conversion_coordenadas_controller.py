from Services.conversion_coordenadas_service import convertir_coordenadas

class ConversionCoordenadasController:
    def __init__(self, view):
        self.view = view

    def convertir(self, sistema_origen, sistema_destino, valores):
        resultado = convertir_coordenadas(sistema_origen, sistema_destino, valores)
        for i, valor in enumerate(resultado):
            if i < len(self.view.destino_campos):
                self.view.destino_campos[i].setText(str(valor))
        # Mostrar el punto en el mapa si hay lat/lon
        if sistema_origen == "Elipsoidal":
            try:
                lat = float(valores[0])
                lon = float(valores[1])
                self.view.mostrar_punto_en_mapa(lat, lon)
            except Exception:
                pass
        elif sistema_destino == "Elipsoidal":
            try:
                lat = float(resultado[0])
                lon = float(resultado[1])
                self.view.mostrar_punto_en_mapa(lat, lon)
            except Exception:
                pass
        return resultado

    def convertir_lote(self, sistema_origen, sistema_destino, datos_origen):
        resultados = []

        # Obtener la zona desde el combobox si el sistema de origen es UTM
        zona = self.view.combo_zona_origen.currentText() if sistema_origen == "UTM" else None

        for valores in datos_origen:
            # Si el sistema de origen es UTM, agrega la zona a los valores
            if sistema_origen == "UTM" and zona:
                valores.append(zona)

            resultado = convertir_coordenadas(sistema_origen, sistema_destino, valores)
            resultados.append(resultado)

        return resultados