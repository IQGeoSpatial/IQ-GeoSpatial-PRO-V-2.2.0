import subprocess
import os
from concurrent.futures import ThreadPoolExecutor

# Logica  de la conversion de GNSS a RINEX
def convertir_gnss_a_rinex(archivos_gnss, version_rinex, sampling_interval, output_obs=True, output_nav=True, output_dir=".", formato="auto"):
    resultados = []
    convbin_path = os.path.abspath(os.path.join("bin", "convbin.exe"))
    output_dir = os.path.abspath(output_dir)

    if not os.path.isfile(convbin_path):
        return [{"success": False, "output_dir": output_dir, "message": f"No se encontró convbin.exe en: {convbin_path}"}]

    def convertir_archivo(archivo_gnss):
        if not os.path.isfile(archivo_gnss):
            return {"success": False, "output_dir": output_dir, "message": f"Archivo GNSS no encontrado: {archivo_gnss}"}

        cmd = [
            convbin_path,
            "-r", formato,                # <-- formato de archivo (ej: auto, ubx, binex, etc.)
            "-v", version_rinex,
            "-os" if output_obs else "-os-",
            "-on" if output_nav else "-on-",
            "-ti", sampling_interval,
            "-d", output_dir,
            archivo_gnss
        ]

        print("Comando ejecutado:", " ".join(cmd))  # Depuración
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            print("STDOUT:", proc.stdout)
            print("STDERR:", proc.stderr)
            if proc.returncode == 0:
                return {"success": True, "output_dir": output_dir, "message": proc.stdout}
            else:
                return {"success": False, "output_dir": output_dir, "message": proc.stderr}
        except Exception as e:
            return {"success": False, "output_dir": output_dir, "message": str(e)}

    with ThreadPoolExecutor(max_workers=2) as executor:
        resultados = list(executor.map(convertir_archivo, archivos_gnss))

    return resultados