from Services import gnss_rinex_service

class GNSSRinexController:
    def __init__(self, view):
        self.view = view

    # Controlador de conversion de GNSS a Rinex
    def convertir_gnss_a_rinex(self, archivos, opciones):
        archivos_gnss = archivos.get("data", [])
        archivos_nav = archivos.get("nav", [])
        version_rinex = opciones.get("rinex_version", "2.11")
        interval = opciones.get("interval", "1")
        output_obs = opciones.get("output_obs", True)
        output_nav = opciones.get("output_nav", True)

        resultados = gnss_rinex_service.convertir_gnss_a_rinex(
            archivos_gnss, version_rinex, interval, output_obs, output_nav, output_dir=opciones["output_dir"]
        )

        if resultados:
            self.view.mostrar_resultado_conversion(resultados[0])
