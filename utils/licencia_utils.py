import hashlib
import uuid
import os
import subprocess
from Models.DataBase import LicenciaDB

HASH_USOS_SECRET = "&IQ20#&25Geo%&Spatial#06/%08_HASH_USOS"
CLAVE_SECRETA = "&IQ20#&25Geo%&Spatial#06/%08"

def hash_usos(valor):
    texto = f"{valor}{HASH_USOS_SECRET}"
    return hashlib.sha256(texto.encode()).hexdigest()

def obtener_mac():
    return str(uuid.getnode())

def obtener_identificador_unico():
    try:
        result = subprocess.check_output(
            'vol C:', shell=True
        ).decode('latin1').split('\n')
        for line in result:
            # Busca "serial" en cualquier idioma/formato
            if "serie" in line.lower():
                # Extrae el valor después de ":"
                id_vol = line.split(":")[-1].strip()
                if id_vol:
                    return id_vol
    except Exception:
        pass
    # Fallback: MAC
    return obtener_mac()

def generar_licencia(nombre_usuario, identificador, clave_secreta=CLAVE_SECRETA):
    texto = nombre_usuario + identificador + clave_secreta
    raw_key = hashlib.sha256(texto.encode()).hexdigest()[:32]
    formatted_key = '-'.join(raw_key[i:i+4] for i in range(0, len(raw_key), 4)).upper()
    return formatted_key

def validar_licencia(nombre_usuario, licencia_ingresada, clave_secreta=CLAVE_SECRETA):
    identificador = obtener_identificador_unico()
    mac_actual = obtener_mac()
    # 1. Validar con identificador único actual
    licencia_id = generar_licencia(nombre_usuario, identificador, clave_secreta)
    if licencia_ingresada.upper() == licencia_id:
        return True
    # 2. Validar con MAC actual (compatibilidad)
    licencia_mac = generar_licencia(nombre_usuario, mac_actual, clave_secreta)
    if licencia_ingresada.upper() == licencia_mac:
        return True
    # 3. Validar con ambos combinados (licencia moderna)
    licencia_combinada = generar_licencia(nombre_usuario, mac_actual + identificador, clave_secreta)
    if licencia_ingresada.upper() == licencia_combinada:
        return True
    # 4. Validar con identificador guardado en la base de datos
    db = LicenciaDB()
    licencia_data = db.cargar_licencia()
    db.close()
    if licencia_data:
        usuario, licencia_guardada, identificador_guardado = licencia_data
        # Validar con identificador guardado
        licencia_id_guardado = generar_licencia(nombre_usuario, identificador_guardado, clave_secreta)
        if licencia_ingresada.upper() == licencia_id_guardado:
            return True
        # Validar con MAC + identificador guardado (por si la MAC cambió)
        licencia_combinada_guardada = generar_licencia(nombre_usuario, mac_actual + identificador_guardado, clave_secreta)
        if licencia_ingresada.upper() == licencia_combinada_guardada:
            return True
    return False

def cargar_estado():
    db = LicenciaDB()
    licencia_data = db.cargar_licencia()
    usos = db.obtener_usos()
    usos_hash = db.obtener_usos_hash() if hasattr(db, 'obtener_usos_hash') else None
    db.close()
    # Validar hash si existe
    if usos_hash is not None:
        if hash_usos(usos) != usos_hash:
            return {"descargas": 99, "licencia": "", "usuario": ""}
    if licencia_data:
        usuario, licencia, identificador_guardado = licencia_data
        return {
            "descargas": usos,
            "licencia": licencia or "",
            "usuario": usuario or "",
            "identificador": identificador_guardado or ""
        }
    return {"descargas": 0, "licencia": "", "usuario": "", "identificador": ""}

def guardar_estado(estado):
    pass

def puede_usar_app():
    """
    Verifica si la aplicación puede ser utilizada, reintroduciendo el modo de prueba.
    1. Si hay una licencia guardada, permite el uso (sin revalidar hardware).
    2. Si no hay licencia, permite un número limitado de usos (modo de prueba).
    """
    estado = cargar_estado()
    
    # Prioridad 1: Verificar si existe una licencia. Si existe, el uso está permitido.
    if estado.get("licencia"):
        return True

    # Prioridad 2: Si no hay licencia, verificar el contador de usos de prueba.
    # Permite 2 usos (cuando el contador es 0 y 1). Al tercer intento (contador=2), se bloquea.
    return estado.get("descargas", 0) < 2

def registrar_uso():
    estado = cargar_estado()
    if not estado.get("licencia"):
        db = LicenciaDB()
        db.registrar_uso()
        if hasattr(db, 'guardar_usos_hash'):
            usos = db.obtener_usos()
            db.guardar_usos_hash(hash_usos(usos))
        db.close()

def ingresar_licencia(nombre_usuario, licencia):
    identificador = obtener_identificador_unico()
    if validar_licencia(nombre_usuario, licencia):
        db = LicenciaDB()
        db.guardar_licencia(nombre_usuario, licencia, identificador)
        db.close()
        return True
    else:
        return False