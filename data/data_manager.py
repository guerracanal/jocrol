import json
import os

DATA_DIR = 'data'
LANZAMIENTOS_FILE = os.path.join(DATA_DIR, 'lanzamientos.json')
EVENTOS_FILE = os.path.join(DATA_DIR, 'eventos.json')
COLECCIONES_FILE = os.path.join(DATA_DIR, 'colecciones.json')
CLIENTES_FILE = os.path.join(DATA_DIR, 'clientes.json')
RESERVAS_FILE = os.path.join(DATA_DIR, 'reservas.json')
STAFF_FILE = os.path.join(DATA_DIR, 'staff.json')

def cargar_datos(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_datos(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
