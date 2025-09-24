from data.data_manager import cargar_datos, STAFF_FILE

def obtener_staff_todos():
    return cargar_datos(STAFF_FILE)
