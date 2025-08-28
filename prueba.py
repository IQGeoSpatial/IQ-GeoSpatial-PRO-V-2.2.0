import subprocess
import sys
import uuid

def obtener_identificador_windows():
    """
    Obtiene el número de serie del volumen C: en Windows de forma robusta
    usando WMIC. Es más fiable que 'vol' porque no depende del idioma.
    """
    try:
        # WMIC es una herramienta de línea de comandos de Windows para WMI.
        # 'get serialnumber' devuelve solo el número de serie.
        command = 'wmic volume where "driveletter=\'c:\'" get serialnumber'
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
        
        # El resultado de WMIC suele tener la cabecera "SerialNumber" y luego el número.
        lines = output.strip().split('\n')
        if len(lines) > 1:
            serial_number = lines[1].strip()
            if serial_number:
                return serial_number
    except (subprocess.CalledProcessError, FileNotFoundError):
        # CalledProcessError si el comando falla, FileNotFoundError si wmic no existe.
        return None
    return None

def obtener_mac_address():
    """
    Obtiene la dirección MAC como un identificador único.
    Es un método multiplataforma.
    """
    try:
        # uuid.getnode() devuelve la dirección MAC como un entero de 48 bits.
        # Lo formateamos como una cadena hexadecimal estándar.
        mac_hex = f'{uuid.getnode():012x}'
        # Formato legible: XX:XX:XX:XX:XX:XX
        return ":".join(mac_hex[i:i+2] for i in range(0, 12, 2)).upper()
    except Exception:
        return None

def obtener_identificador_unico():
    """
    Intenta obtener un identificador único del sistema.
    
    Prueba varios métodos en orden de preferencia:
    1. Número de serie del volumen en Windows (muy estable para una máquina).
    2. Dirección MAC (buen identificador de hardware, multiplataforma).
    
    Devuelve el primer identificador que encuentre o None si todos fallan.
    """
    identificador = None
    
    # Si es Windows, intentar primero con el número de serie del volumen.
    if sys.platform == "win32":
        identificador = obtener_identificador_windows()

    # Si el primer método falló o no es Windows, usar la dirección MAC.
    if not identificador:
        identificador = obtener_mac_address()

    return identificador

if __name__ == '__main__':
    id_unico = obtener_identificador_unico()
    if id_unico:
        print(f"Identificador único obtenido: {id_unico}")
    else:
        print("No se pudo obtener un identificador único.")