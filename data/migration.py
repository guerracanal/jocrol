
import json
import os
from data.data_manager import (
    LANZAMIENTOS_COLLECTION,
    EVENTOS_COLLECTION,
    CLIENTES_COLLECTION,
    RESERVAS_COLLECTION,
    STAFF_COLLECTION,
    JUEGOS_COLECCIONES_COLLECTION,
    guardar_datos
)

DATA_DIR = 'data'
LANZAMIENTOS_FILE = os.path.join(DATA_DIR, 'lanzamientos.json')
EVENTOS_FILE = os.path.join(DATA_DIR, 'eventos.json')
CLIENTES_FILE = os.path.join(DATA_DIR, 'clientes.json')
RESERVAS_FILE = os.path.join(DATA_DIR, 'reservas.json')
STAFF_FILE = os.path.join(DATA_DIR, 'staff.json')
JUEGOS_COLECCIONES_FILE = os.path.join(DATA_DIR, 'juegos_colecciones.json')

def migrar_datos():
    with open(LANZAMIENTOS_FILE, 'r', encoding='utf-8') as f:
        lanzamientos_data = json.load(f)
    guardar_datos(LANZAMIENTOS_COLLECTION, lanzamientos_data)

    with open(EVENTOS_FILE, 'r', encoding='utf-8') as f:
        eventos_data = json.load(f)
    guardar_datos(EVENTOS_COLLECTION, eventos_data)

    with open(CLIENTES_FILE, 'r', encoding='utf-8') as f:
        clientes_data = json.load(f)
    guardar_datos(CLIENTES_COLLECTION, clientes_data)

    with open(RESERVAS_FILE, 'r', encoding='utf-8') as f:
        reservas_data = json.load(f)
    guardar_datos(RESERVAS_COLLECTION, reservas_data)

    with open(STAFF_FILE, 'r', encoding='utf-8') as f:
        staff_data = json.load(f)
    guardar_datos(STAFF_COLLECTION, staff_data)

    with open(JUEGOS_COLECCIONES_FILE, 'r', encoding='utf-8') as f:
        juegos_colecciones_json = json.load(f)
    
    juegos_colecciones_data = []
    for nombre, datos in juegos_colecciones_json["juegos"].items():
        juegos_colecciones_data.append({
            "nombre": nombre,
            "color": datos["color"],
            "colecciones": datos["colecciones"]
        })
    guardar_datos(JUEGOS_COLECCIONES_COLLECTION, juegos_colecciones_data)

if __name__ == '__main__':
    migrar_datos()
