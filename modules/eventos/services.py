from data.data_manager import (
    cargar_datos, 
    guardar_datos, 
    EVENTOS_FILE,
    cargar_juegos_colecciones
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
    return cargar_juegos_colecciones()

def obtener_eventos_todos():
    return cargar_datos(EVENTOS_FILE)

def obtener_eventos_filtrados(filters):
    eventos_todos = obtener_eventos_todos()
    juegos_data = obtener_juegos_y_colecciones().get('juegos', {})
    
    eventos_filtrados = eventos_todos

    q = filters.get('q')
    if q:
        q = q.lower()
        eventos_filtrados = [
            e for e in eventos_filtrados 
            if q in e.get('nombre', '').lower() or \
               q in e.get('coleccion', '').lower() or \
               q in e.get('juego', '').lower()
        ]
    
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
            
    eventos_filtrados.sort(key=lambda x: x.get('fecha') or '', reverse=True)
    
    return eventos_filtrados

def obtener_evento_por_id(evento_id):
    evento = next((e for e in obtener_eventos_todos() if e.get('id') == evento_id), None)
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
    eventos = obtener_eventos_todos()
    nuevo_id = generar_id()
    evento = {
        "id": nuevo_id,
        "nombre": datos_evento.get('nombre'),
        "juego": datos_evento.get('juego'),
        "coleccion": datos_evento.get('coleccion'),
        "fecha_salida": datos_evento.get('fecha_salida'),
        "precio": float(datos_evento.get('precio') or 0),
        "reserva": float(datos_evento.get('reserva') or 0),
        "tipo": "Evento",
        "comentario": datos_evento.get('comentario', ''),
        "fecha": datos_evento.get('fecha_salida')
    }
    eventos.append(evento)
    guardar_datos(EVENTOS_FILE, eventos)

def actualizar_evento(evento_id, datos_evento):
    eventos = obtener_eventos_todos()
    for i, e in enumerate(eventos):
        if e.get('id') == evento_id:
            e['nombre'] = datos_evento.get('nombre', e.get('nombre'))
            e['juego'] = datos_evento.get('juego', e.get('juego'))
            e['coleccion'] = datos_evento.get('coleccion', e.get('coleccion'))
            e['fecha_salida'] = datos_evento.get('fecha_salida', e.get('fecha_salida'))
            e['precio'] = float(datos_evento.get('precio') or e.get('precio') or 0)
            e['reserva'] = float(datos_evento.get('reserva') or e.get('reserva') or 0)
            e['comentario'] = datos_evento.get('comentario', e.get('comentario'))
            e['fecha'] = datos_evento.get('fecha_salida', e.get('fecha_salida'))
            break
    guardar_datos(EVENTOS_FILE, eventos)

def eliminar_evento(evento_id):
    eventos = obtener_eventos_todos()
    eventos_filtrados = [e for e in eventos if e.get('id') != evento_id]
    guardar_datos(EVENTOS_FILE, eventos_filtrados)
