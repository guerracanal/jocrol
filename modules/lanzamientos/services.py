from data.data_manager import (
    LANZAMIENTOS_COLLECTION, 
    RESERVAS_COLLECTION, 
    CLIENTES_COLLECTION, 
    JUEGOS_COLECCIONES_COLLECTION
)
from collections import defaultdict
from datetime import datetime
import uuid

def adjust_color_brightness(hex_color, factor):
    """
    Ajusta el brillo de un color hexadecimal.
    Factor < 1 para oscurecer, > 1 para aclarar.
    """
    if not hex_color or not hex_color.startswith('#') or len(hex_color) != 7:
        return hex_color
    
    try:
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        r = int(max(0, min(255, r * factor)))
        g = int(max(0, min(255, g * factor)))
        b = int(max(0, min(255, b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    except (ValueError, TypeError):
        return hex_color

def generar_id():
    return str(uuid.uuid4())

def obtener_juegos_y_colecciones():
    juegos_list = list(JUEGOS_COLECCIONES_COLLECTION.find({}, {'_id': 0}))
    juegos_dict = {
        juego['nombre']: {
            'color': juego['color'],
            'colecciones': juego['colecciones']
        }
        for juego in juegos_list
    }
    return {'juegos': juegos_dict}

def obtener_lanzamientos_todos():
    return list(LANZAMIENTOS_COLLECTION.find({}, {'_id': 0}))

def obtener_reservas_todas():
    return list(RESERVAS_COLLECTION.find({}, {'_id': 0}))

def obtener_clientes_todos():
    return list(CLIENTES_COLLECTION.find({}, {'_id': 0}))

def obtener_lanzamiento_por_id(lanzamiento_id):
    lanzamiento = LANZAMIENTOS_COLLECTION.find_one({'id': lanzamiento_id}, {'_id': 0})
    if lanzamiento:
        juego_info = JUEGOS_COLECCIONES_COLLECTION.find_one({'nombre': lanzamiento.get('juego')}, {'_id': 0})
        if juego_info:
            lanzamiento['juego_color'] = juego_info.get('color', '#6c757d')
        else:
            lanzamiento['juego_color'] = '#6c757d'
    return lanzamiento

def obtener_lanzamientos_filtrados(filters):
    pipeline = []
    match_stage = {}

    q = filters.get('q')
    if q:
        q = q.lower()
        match_stage['$or'] = [
            {'nombre': {'$regex': q, '$options': 'i'}},
            {'coleccion': {'$regex': q, '$options': 'i'}},
            {'juego': {'$regex': q, '$options': 'i'}}
        ]

    if filters.get('juego'):
        match_stage['juego'] = filters.get('juego')

    if filters.get('start_date'):
        match_stage['fecha_salida'] = {'$gte': filters.get('start_date')}

    if filters.get('end_date'):
        if 'fecha_salida' not in match_stage:
            match_stage['fecha_salida'] = {}
        match_stage['fecha_salida']['$lte'] = filters.get('end_date')

    if filters.get('hide_past') == 'on':
        today = datetime.now().strftime('%Y-%m-%d')
        if 'fecha_salida' not in match_stage:
            match_stage['fecha_salida'] = {}
        match_stage['fecha_salida']['$gte'] = today

    if match_stage:
        pipeline.append({'$match': match_stage})

    sort_by = filters.get('sort_by') or 'fecha_salida'
    sort_order = 1 if filters.get('sort_order', 'asc') == 'asc' else -1
    pipeline.append({'$sort': {sort_by: sort_order, '_id': 1}})

    lanzamientos_filtrados = list(LANZAMIENTOS_COLLECTION.aggregate(pipeline))
    lanz_ids = [l['id'] for l in lanzamientos_filtrados]

    reservas_por_lanzamiento = defaultdict(list)
    cliente_ids = set()
    if lanz_ids:
        reservas_cursor = RESERVAS_COLLECTION.find({'lanzamiento_id': {'$in': lanz_ids}})
        for r in reservas_cursor:
            reservas_por_lanzamiento[r['lanzamiento_id']].append(r)
            if r.get('cliente_id'):
                cliente_ids.add(r['cliente_id'])

    clientes_map = {}
    if cliente_ids:
        clientes_cursor = CLIENTES_COLLECTION.find({'id': {'$in': list(cliente_ids)}})
        clientes_map = {c['id']: c for c in clientes_cursor}

    for lanz_id, reservas in reservas_por_lanzamiento.items():
        for r in reservas:
            if r.get('cliente_id') in clientes_map:
                r['cliente'] = clientes_map[r['cliente_id']]

    juegos_data = obtener_juegos_y_colecciones().get('juegos', {})
    for lanz in lanzamientos_filtrados:
        lanz['reservas'] = reservas_por_lanzamiento.get(lanz.get('id'), [])
        juego_nombre = lanz.get('juego')
        coleccion_nombre = lanz.get('coleccion')
        
        if juego_nombre and juego_nombre in juegos_data:
            juego_info = juegos_data[juego_nombre]
            juego_color = juego_info.get('color', '#6c757d')
            lanz['juego_color'] = juego_color
            
            colecciones = juego_info.get('colecciones', [])
            if coleccion_nombre and coleccion_nombre in colecciones:
                try:
                    idx = colecciones.index(coleccion_nombre)
                    factor = 1 - ((idx + 1) * 0.1)
                    lanz['coleccion_color'] = adjust_color_brightness(juego_color, factor)
                except (ValueError, TypeError):
                    lanz['coleccion_color'] = juego_color
            else:
                lanz['coleccion_color'] = juego_color
        else:
            lanz['juego_color'] = '#6c757d'
            lanz['coleccion_color'] = '#6c757d'

    return lanzamientos_filtrados, juegos_data

def crear_lanzamiento(datos_lanzamiento):
    nuevo_id = generar_id()
    lanzamiento = {
        "id": nuevo_id,
        "nombre": datos_lanzamiento.get('nombre'),
        "juego": datos_lanzamiento.get('juego'),
        "coleccion": datos_lanzamiento.get('coleccion'),
        "fecha_salida": datos_lanzamiento.get('fecha_salida'),
        "fecha_envio": datos_lanzamiento.get('fecha_envio'),
        "precio": float(datos_lanzamiento.get('precio') or 0),
        "precio_reserva": float(datos_lanzamiento.get('precio_reserva') or 0),
        "comentario": datos_lanzamiento.get('comentario'),
    }
    LANZAMIENTOS_COLLECTION.insert_one(lanzamiento)

def actualizar_lanzamiento(lanzamiento_id, datos_lanzamiento):
    update_data = {
        "nombre": datos_lanzamiento.get('nombre'),
        "juego": datos_lanzamiento.get('juego'),
        "coleccion": datos_lanzamiento.get('coleccion'),
        "fecha_salida": datos_lanzamiento.get('fecha_salida'),
        "fecha_envio": datos_lanzamiento.get('fecha_envio'),
        "precio": float(datos_lanzamiento.get('precio') or 0),
        "precio_reserva": float(datos_lanzamiento.get('precio_reserva') or 0),
        "comentario": datos_lanzamiento.get('comentario'),
    }
    result = LANZAMIENTOS_COLLECTION.update_one({'id': lanzamiento_id}, {'$set': update_data})
    if result.matched_count == 0:
        raise ValueError(f"No se encontró el lanzamiento con ID {lanzamiento_id}")

def eliminar_lanzamiento(lanzamiento_id):
    delete_result = LANZAMIENTOS_COLLECTION.delete_one({'id': lanzamiento_id})
    if delete_result.deleted_count == 0:
        raise ValueError(f"No se encontró el lanzamiento con ID {lanzamiento_id}")
    
    RESERVAS_COLLECTION.delete_many({'lanzamiento_id': lanzamiento_id})
