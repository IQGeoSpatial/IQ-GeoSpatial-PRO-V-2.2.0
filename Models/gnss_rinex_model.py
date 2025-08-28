class GNSSRinexConversion:
    def __init__(self, archivo_gnss, archivo_nav, version_rinex, interval, output_obs, output_nav):
        self.archivo_gnss = archivo_gnss
        self.archivo_nav = archivo_nav
        self.version_rinex = version_rinex
        self.interval = interval
        self.output_obs = output_obs
        self.output_nav = output_nav
        self.resultado = None