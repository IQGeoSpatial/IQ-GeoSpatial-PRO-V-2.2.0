# # Models/validation_model.py

# """
# Define la estructura canónica y los alias para la validación de expedientes.
# - 'name': El nombre oficial o canónico que aparecerá en el reporte.
# - 'type': 'folder' o 'file'.
# - 'aliases': Una lista de posibles nombres (sin prefijos numéricos y normalizados)
#              que el validador buscará. La normalización implica convertir a
#              minúsculas y reemplazar espacios y guiones bajos.
# - 'optional': Booleano que indica si el elemento es opcional.
# - 'children': Una lista de otros diccionarios para elementos anidados (solo para carpetas).
# """


EXPEDIENTE_STRUCTURE = {
    "name": "ROOT_EXPEDIENTE",
    "type": "folder",
    "aliases": [],
    "optional": False,
    "children": [
        {
            "name": "1. FORMULARIOS",
            "type": "folder",
            "aliases": ["formularios"],
            "optional": False,
            "children": [
                {
                    "name": "INFORME GENERAL.pdf",
                    "type": "file",
                    "aliases": ["informegeneral.pdf", "informe.pdf"],
                    "optional": False,
                    "children": []
                }
            ]
        },
        {
            "name": "2. DATOS_GNSS",
            "type": "folder",
            "aliases": ["datosgnss"],
            "optional": False,
            # 👇 Habilita validación de carpetas dinámicas [CODIGO_PUNTO_GEODESICO]
            "allow_dynamic_points": True,
            "children": [
                {
                    "name": "1. Datos de la Estación Base",
                    "type": "folder",
                    "aliases": ["datosdelaestacionbase", "datosestacionbase"],
                    "optional": False,
                    "children": [
                        {"name": "Nativo", "type": "folder", "aliases": ["nativo"], "optional": False, "children": []},
                        {"name": "RINEX", "type": "folder", "aliases": ["rinex"], "optional": False, "children": []},
                        {"name": "Descripcion_Monografica_ERP.pdf", "type": "file", "aliases": ["descripcionmonograficaerp.pdf", "fichaerp.pdf"], "optional": False, "children": []},
                        {"name": "Certificado_Punto_Base.pdf", "type": "file", "aliases": ["certificadopuntobase.pdf"], "optional": True, "children": []},
                    ]
                },
                {
                    "name": "2. Efemerides",
                    "type": "folder",
                    "aliases": ["efemerides", "efemeridesempleadas"],
                    "optional": False,
                    "children": [
                        # Acepta cualquier archivo .sp3
                        {"name": "Efemerides_Procesamiento.SP3", "type": "file", "aliases": ["*.sp3", "*.sp3.gz"], "optional": False, "children": []}
                    ]
                },
                {
                    "name": "3. Procesamiento",
                    "type": "folder",
                    "aliases": ["procesamiento"],
                    "optional": False,
                    "children": [
                        # La carpeta puede llamarse con o sin guiones/espacios/“de”
                        {"name": "Carpetas_Software_Procesamiento", "type": "folder",
                         "aliases": ["carpetassoftwareprocesamiento", "carpetasdesoftwaredeprocesamiento", "carpetassoftware", "carpetassoftwareprocesamiento"],
                         "optional": False, "children": []},
                        {"name": "Reporte_Procesamiento.pdf", "type": "file", "aliases": ["reporteprocesamiento.pdf"], "optional": False, "children": []}
                    ]
                },
                {"name": "Manual_Equipo_GNSS.pdf", "type": "file", "aliases": ["manualequipognss.pdf", "manualdeequipognss.pdf", "manualdeequipos.pdf"], "optional": False, "children": []},
                {"name": "Sustento_Altura_Antena.pdf", "type": "file", "aliases": ["sustentoalturaantena.pdf"], "optional": True, "children": []},
            ]
        },
        {
            "name": "3. FOTOGRAFIAS",
            "type": "folder",
            "aliases": ["fotografias", "fotos"],
            "optional": False,
            "children": [
                {"name": "01. Equipo GNSS", "type": "folder", "aliases": ["equipognss", "fotosreceptorgnss"], "optional": False, "children": []},
                {"name": "02. Proceso de Monumentacion", "type": "folder", "aliases": ["procesodemonumentacion"], "optional": False, "children": []},
                {"name": "03. Profundidad", "type": "folder", "aliases": ["profundidad"], "optional": False, "children": []},
                {"name": "04. Anclaje de Disco de Bronce", "type": "folder", "aliases": ["anclajedediscodebronce", "anclajedisco"], "optional": False, "children": []},
                {"name": "05. Incrustacion del Disco de Bronce", "type": "folder", "aliases": ["incrustaciondeldiscodebronce", "incrustaciondisco"], "optional": False, "children": []},
                {"name": "06. Disco Instalado", "type": "folder", "aliases": ["discoinstalado"], "optional": False, "children": []},
                {"name": "07. Medicion de Altura de Antena", "type": "folder", "aliases": ["mediciondealturadeantena", "fotosalturadeantena"], "optional": False, "children": []},
                {"name": "08. Fotografías Panoramicas", "type": "folder", "aliases": ["fotografiaspanoramicas", "fotospanoramicas"], "optional": False, "children": []},
                {"name": "09. Videos", "type": "folder", "aliases": ["videos"], "optional": True, "children": []},
            ]
        },
        {
            "name": "4. VERIFICACION_COORDENADAS",
            "type": "folder",
            "aliases": ["verificacioncoordenadas"],
            "optional": True,
            "children": []
        },

        {
        "name": "4. VERIFICACION_COORDENADAS",
        "type": "folder",
        "aliases": ["verificacioncoordenadas", "resultadosvalidacion"],
        "optional": False,   # 👈 Ahora siempre se valida
        "children": [
            {"name": "Certificado de PG.pdf", "type": "file", "aliases": ["certificadopg.pdf"], "optional": False, "children": []},
            {"name": "Carta Poder.pdf", "type": "file", "aliases": ["cartapoder.pdf"], "optional": False, "children": []},
            {"name": "Diario de OBS.pdf", "type": "file", "aliases": ["diariodeobs.pdf"], "optional": False, "children": []},
            {"name": "Certificado de Operatividad.pdf", "type": "file", "aliases": ["certificadodeoperatividad.pdf"], "optional": False, "children": []},
            {"name": "Reporte de Procesamiento.pdf", "type": "file", "aliases": ["reporteprocesamiento.pdf"], "optional": False, "children": []},

            {
                "name": "Datos Estación Base",
                "type": "folder",
                "aliases": ["datosestacionbase"],
                "optional": False,
                "children": [
                    {"name": "Nativa", "type": "folder", "aliases": ["nativa"], "optional": False, "children": []},
                    {"name": "RINEX", "type": "folder", "aliases": ["rinex"], "optional": False, "children": []}
                ]
            },
            {
                "name": "Datos GNSS",
                "type": "folder",
                "aliases": ["datosgnss"],
                "optional": False,
                "children": [
                    {"name": "Nativo", "type": "folder", "aliases": ["nativo"], "optional": False, "children": []},
                    {"name": "RINEX", "type": "folder", "aliases": ["rinex"], "optional": False, "children": []},
                    {"name": "PROCESAMIENTO", "type": "folder", "aliases": ["procesamiento"], "optional": False, "children": []},
                    {"name": "Conversion de altur.pdf", "type": "file", "aliases": ["conversiondealtura.pdf"], "optional": False, "children": []},
                    {"name": "Manual de equipo.pdf", "type": "file", "aliases": ["manualdeequipognss.pdf"], "optional": False, "children": []},
                ]
            },
            {"name": "Fichas ERP", "type": "folder", "aliases": ["fichaserp"], "optional": False, "children": []},
            {"name": "Efemerides Empleadas", "type": "folder", "aliases": ["efemeridesempleadas"], "optional": False, "children": []},
            {"name": "Fotos Receptor GNSS", "type": "folder", "aliases": ["fotosreceptorgnss"], "optional": False, "children": []},
            {"name": "Fotos Altura de Antena", "type": "folder", "aliases": ["fotosalturadeantena"], "optional": False, "children": []},
            {"name": "Fotos Panoramicas", "type": "folder", "aliases": ["fotospanoramicas"], "optional": False, "children": []},
            {"name": "Recibos De Ingreso", "type": "folder", "aliases": ["recibosdeingreso"], "optional": False, "children": []},
            {"name": "Resultados Validacion", "type": "folder", "aliases": ["resultadosvalidacion"], "optional": False, "children": []},
            ]
        }
    ]
}
