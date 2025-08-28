def detectar_tipo_gnss(archivo):
    if archivo.endswith(".dat"):
        return "Trimble"
    elif archivo.endswith(".T01"):
        return "South"
    elif archivo.endswith(".chc"):
        return "CHC"
    else:
        return "Desconocido"