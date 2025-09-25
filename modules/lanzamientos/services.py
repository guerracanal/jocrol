from data.data_manager import (
    cargar_datos, 
    guardar_datos, 
    LANZAMIENTOS_FILE, 
    RESERVAS_FILE, 
    CLIENTES_FILE, 
    cargar_juegos_colecciones
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
    return cargar_juegos_colecciones()

def obtener_lanzamientos_todos():
    return cargar_datos(LANZAMIENTOS_FILE)

def obtener_reservas_todas():
    return cargar_datos(RESERVAS_FILE)

def obtener_clientes_todos():
    return cargar_datos(CLIENTES_FILE)

def obtener_lanzamiento_por_id(lanzamiento_id):
    lanzamiento = next((l for l in obtener_lanzamientos_todos() if l.get('id') == lanzamiento_id), None)
    if lanzamiento:
        juegos_data = obtener_juegos_y_colecciones().get('juegos', {})
        juego_nombre = lanzamiento.get('juego')
        if juego_nombre and juego_nombre in juegos_data:
            lanzamiento['juego_color'] = juegos_data[juego_nombre].get('color', '#6c757d')
        else:
            lanzamiento['juego_color'] = '#6c757d'
    return lanzamiento

def obtener_lanzamientos_filtrados(filters):
    lanzamientos_todos = obtener_lanzamientos_todos()
    reservas = obtener_reservas_todas()
    clientes = {c['id']: c for c in obtener_clientes_todos()}
    juegos_data = obtener_juegos_y_colecciones().get('juegos', {})

    lanzamientos_filtrados = lanzamientos_todos

    q = filters.get('q')
    if q:
        q = q.lower()
        lanzamientos_filtrados = [
            l for l in lanzamientos_filtrados 
            if q in l.get('nombre', '').lower() or \
               q in l.get('coleccion', '').lower() or \
               q in l.get('juego', '').lower()
        ]
    
    juego_filter = filters.get('juego')
    if juego_filter:
        lanzamientos_filtrados = [l for l in lanzamientos_filtrados if l.get('juego') == juego_filter]

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
    
    lanzamientos_filtrados.sort(key=lambda x: (x.get(sort_by) is None, x.get(sort_by, 0)), reverse=reverse)

    reservas_por_lanzamiento = defaultdict(list)
    for res in reservas:
        res['cliente'] = clientes.get(res.get('cliente_id'))
        reservas_por_lanzamiento[res.get('lanzamiento_id')].append(res)

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
    lanzamientos = obtener_lanzamientos_todos()
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
    lanzamientos.append(lanzamiento)
    guardar_datos(LANZAMIENTOS_FILE, lanzamientos)

def actualizar_lanzamiento(lanzamiento_id, datos_lanzamiento):
    lanzamientos = obtener_lanzamientos_todos()
    for i, lanz in enumerate(lanzamientos):
        if lanz.get('id') == lanzamiento_id:
            lanzamientos[i] = {
                "id": lanzamiento_id,
                "nombre": datos_lanzamiento.get('nombre'),
                "juego": datos_lanzamiento.get('juego'),
                "coleccion": datos_lanzamiento.get('coleccion'),
                "fecha_salida": datos_lanzamiento.get('fecha_salida'),
                "fecha_envio": datos_lanzamiento.get('fecha_envio'),
                "precio": float(datos_lanzamiento.get('precio') or 0),
                "precio_reserva": float(datos_lanzamiento.get('precio_reserva') or 0),
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
