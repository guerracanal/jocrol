from data.data_manager import (
    EVENTOS_COLLECTION,
    JUEGOS_COLECCIONES_COLLECTION,
    RESERVAS_COLLECTION
)
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

def obtener_eventos_todos():
    return list(EVENTOS_COLLECTION.find({}, {'_id': 0}))

def obtener_eventos_filtrados(filters):
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
    
    if match_stage:
        pipeline.append({'$match': match_stage})

    pipeline.append({'$sort': {'fecha': -1, '_id': 1}})
    pipeline.append({'$project': {'_id': 0}})

    eventos_filtrados = list(EVENTOS_COLLECTION.aggregate(pipeline))
    
    juegos_data = obtener_juegos_y_colecciones().get('juegos', {})
    
    for evento in eventos_filtrados:
        juego_nombre = evento.get('juego')
        coleccion_nombre = evento.get('coleccion')
        
        if juego_nombre and juego_nombre in juegos_data:
            juego_info = juegos_data[juego_nombre]
            juego_color = juego_info.get('color', '#6c757d')
            evento['juego_color'] = juego_color
            
            colecciones = juego_info.get('colecciones', [])
            if coleccion_nombre and coleccion_nombre in colecciones:
                try:
                    idx = colecciones.index(coleccion_nombre)
                    factor = 1 - ((idx + 1) * 0.1)
                    evento['coleccion_color'] = adjust_color_brightness(juego_color, factor)
                except (ValueError, TypeError):
                    evento['coleccion_color'] = juego_color
            else:
                evento['coleccion_color'] = juego_color
        else:
            evento['juego_color'] = '#6c757d'
            evento['coleccion_color'] = '#6c757d'
            
    return eventos_filtrados

def obtener_evento_por_id(evento_id):
    evento = EVENTOS_COLLECTION.find_one({'id': evento_id}, {'_id': 0})
    if evento:
        juegos_data = obtener_juegos_y_colecciones().get('juegos', {})
        juego_nombre = evento.get('juego')
        coleccion_nombre = evento.get('coleccion')
        
        if juego_nombre and juego_nombre in juegos_data:
            juego_info = juegos_data[juego_nombre]
            juego_color = juego_info.get('color', '#6c757d')
            evento['juego_color'] = juego_color
            
            colecciones = juego_info.get('colecciones', [])
            if coleccion_nombre and coleccion_nombre in colecciones:
                try:
                    idx = colecciones.index(coleccion_nombre)
                    factor = 1 - ((idx + 1) * 0.1)
                    evento['coleccion_color'] = adjust_color_brightness(juego_color, factor)
                except (ValueError, TypeError):
                    evento['coleccion_color'] = juego_color
            else:
                evento['coleccion_color'] = juego_color
        else:
            evento['juego_color'] = '#6c757d'
            evento['coleccion_color'] = '#6c757d'

    return evento

def crear_evento(datos_evento):
    nuevo_id = generar_id()
    evento = {
        "id": nuevo_id,
        "nombre": datos_evento.get('nombre'),
        "juego": datos_evento.get('juego'),
        "coleccion": datos_evento.get('coleccion'),
        "fecha_salida": datos_evento.get('fecha_salida'),
        "precio": float(datos_evento.get('precio') or 0),
        "precio_reserva": float(datos_evento.get('reserva') or 0),
        "tipo": "Evento",
        "comentario": datos_evento.get('comentario', ''),
        "fecha": datos_evento.get('fecha_salida')
    }
    EVENTOS_COLLECTION.insert_one(evento)

def actualizar_evento(evento_id, datos_evento):
    update_data = {
        'nombre': datos_evento.get('nombre'),
        'juego': datos_evento.get('juego'),
        'coleccion': datos_evento.get('coleccion'),
        'fecha_salida': datos_evento.get('fecha_salida'),
        'precio': float(datos_evento.get('precio') or 0),
        'precio_reserva': float(datos_evento.get('reserva') or 0),
        'comentario': datos_evento.get('comentario', ''),
        'fecha': datos_evento.get('fecha_salida')
    }
    result = EVENTOS_COLLECTION.update_one({'id': evento_id}, {'$set': update_data})
    if result.matched_count == 0:
        raise ValueError(f"No se encontró el evento con ID {evento_id}")

def eliminar_evento(evento_id):
    if RESERVAS_COLLECTION.find_one({'evento_id': evento_id}):
        raise ValueError("No se puede eliminar un evento que tiene reservas asociadas.")
        
    result = EVENTOS_COLLECTION.delete_one({'id': evento_id})
    if result.deleted_count == 0:
        raise ValueError(f"No se encontró el evento con ID {evento_id}")
