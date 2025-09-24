from data.data_manager import cargar_datos, guardar_datos, LANZAMIENTOS_FILE, RESERVAS_FILE, CLIENTES_FILE, COLECCIONES_FILE
from collections import defaultdict
from datetime import datetime
import random
import uuid

def generar_id():
    return str(uuid.uuid4())

def obtener_lanzamientos_todos():
    return cargar_datos(LANZAMIENTOS_FILE)

def obtener_reservas_todas():
    return cargar_datos(RESERVAS_FILE)

def obtener_clientes_todos():
    return cargar_datos(CLIENTES_FILE)

def obtener_colecciones_todas():
    return cargar_datos(COLECCIONES_FILE)

def obtener_lanzamiento_por_id(lanzamiento_id):
    lanzamientos = obtener_lanzamientos_todos()
    for lanz in lanzamientos:
        if lanz.get('id') == lanzamiento_id:
            return lanz
    return None

def obtener_lanzamientos_filtrados(filters):
    lanzamientos_todos = obtener_lanzamientos_todos()
    reservas = obtener_reservas_todas()
    clientes = {c['id']: c for c in obtener_clientes_todos()}
    colecciones = {c['nombre']: c for c in obtener_colecciones_todas()}

    lanzamientos_filtrados = lanzamientos_todos

    if filters.get('q'):
        q = filters['q'].lower()
        lanzamientos_filtrados = [
            l for l in lanzamientos_filtrados 
            if q in l.get('nombre', '').lower() or q in l.get('coleccion', '').lower()
        ]

    if filters.get('start_date'):
        lanzamientos_filtrados = [l for l in lanzamientos_filtrados if l.get('fecha_salida') >= filters['start_date']]

    if filters.get('end_date'):
        lanzamientos_filtrados = [l for l in lanzamientos_filtrados if l.get('fecha_salida') <= filters['end_date']]

    if filters.get('hide_past') == 'on':
        today = datetime.now().strftime('%Y-%m-%d')
        lanzamientos_filtrados = [l for l in lanzamientos_filtrados if l.get('fecha_salida') >= today]

    sort_by = filters.get('sort_by', 'fecha_salida')
    sort_order = filters.get('sort_order', 'asc')
    reverse = sort_order == 'desc'
    
    # Handle missing values for sorting
    lanzamientos_filtrados = sorted(lanzamientos_filtrados, key=lambda x: (x.get(sort_by) is None, x.get(sort_by, 0)), reverse=reverse)

    reservas_por_lanzamiento = defaultdict(list)
    for res in reservas:
        res['cliente'] = clientes.get(res.get('cliente_id'))
        reservas_por_lanzamiento[res.get('lanzamiento_id')].append(res)

    for lanz in lanzamientos_filtrados:
        lanz['reservas'] = reservas_por_lanzamiento.get(lanz.get('id'), [])
        lanz['coleccion_data'] = colecciones.get(lanz.get('coleccion'))

    return lanzamientos_filtrados, list(colecciones.values())

def _crear_coleccion_si_no_existe(nombre_coleccion):
    colecciones = obtener_colecciones_todas()
    if not any(c['nombre'] == nombre_coleccion for c in colecciones):
        nueva_coleccion = {
            "nombre": nombre_coleccion,
            "color": f'#{random.randint(0, 0xFFFFFF):06x}'
        }
        colecciones.append(nueva_coleccion)
        guardar_datos(COLECCIONES_FILE, colecciones)

def crear_lanzamiento(datos_lanzamiento):
    _crear_coleccion_si_no_existe(datos_lanzamiento.get('coleccion'))
    lanzamientos = obtener_lanzamientos_todos()
    nuevo_id = generar_id()
    lanzamiento = {
        "id": nuevo_id,
        "nombre": datos_lanzamiento.get('nombre'),
        "coleccion": datos_lanzamiento.get('coleccion'),
        "fecha_salida": datos_lanzamiento.get('fecha_salida'),
        "fecha_envio": datos_lanzamiento.get('fecha_envio'),
        "precio": float(datos_lanzamiento.get('precio') or 0),
        "reserva": float(datos_lanzamiento.get('reserva') or 0),
        "comentario": datos_lanzamiento.get('comentario'),
    }
    lanzamientos.append(lanzamiento)
    guardar_datos(LANZAMIENTOS_FILE, lanzamientos)

def actualizar_lanzamiento(lanzamiento_id, datos_lanzamiento):
    _crear_coleccion_si_no_existe(datos_lanzamiento.get('coleccion'))
    lanzamientos = obtener_lanzamientos_todos()
    for i, lanz in enumerate(lanzamientos):
        if lanz.get('id') == lanzamiento_id:
            lanzamientos[i] = {
                "id": lanzamiento_id,
                "nombre": datos_lanzamiento.get('nombre'),
                "coleccion": datos_lanzamiento.get('coleccion'),
                "fecha_salida": datos_lanzamiento.get('fecha_salida'),
                "fecha_envio": datos_lanzamiento.get('fecha_envio'),
                "precio": float(datos_lanzamiento.get('precio') or 0),
                "reserva": float(datos_lanzamiento.get('reserva') or 0),
                "comentario": datos_lanzamiento.get('comentario'),
            }
            break
    guardar_datos(LANZAMIENTOS_FILE, lanzamientos)

def eliminar_lanzamiento(lanzamiento_id):
    lanzamientos = obtener_lanzamientos_todos()
    lanzamientos_filtrados = [l for l in lanzamientos if l.get('id') != lanzamiento_id]
    guardar_datos(LANZAMIENTOS_FILE, lanzamientos_filtrados)

    reservas = obtener_reservas_todas()
    reservas_filtradas = [r for r in reservas if r.get('lanzamiento_id') != lanzamiento_id]
    guardar_datos(RESERVAS_FILE, reservas_filtradas)
