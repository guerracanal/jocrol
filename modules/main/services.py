from data.data_manager import (
    LANZAMIENTOS_COLLECTION,
    EVENTOS_COLLECTION
)
from modules.eventos.services import obtener_juegos_y_colecciones

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

def obtener_eventos_calendario():
    try:
        lanzamientos = list(LANZAMIENTOS_COLLECTION.find({}, {'_id': 0}))
        eventos_data = list(EVENTOS_COLLECTION.find({}, {'_id': 0}))
        juegos_data = obtener_juegos_y_colecciones().get('juegos', {})

        eventos_calendario = []

        for lanz in lanzamientos:
            juego_nombre = lanz.get('juego')
            coleccion_nombre = lanz.get('coleccion')
            juego_info = juegos_data.get(juego_nombre, {})
            juego_color = juego_info.get('color', '#6c757d')
            
            colecciones = juego_info.get('colecciones', [])
            coleccion_color = juego_color
            if coleccion_nombre and coleccion_nombre in colecciones:
                try:
                    idx = colecciones.index(coleccion_nombre)
                    factor = 1 - ((idx + 1) * 0.1)
                    coleccion_color = adjust_color_brightness(juego_color, factor)
                except (ValueError, TypeError):
                    pass

            juego_inicial_badge = f'<span class="badge" style="background-color: {juego_color};">{juego_nombre[0] if juego_nombre else " "}</span>'

            eventos_calendario.append({
                'id': f"salida-{lanz.get('id')}",
                'title': f'{juego_inicial_badge} 🚀 {lanz.get("nombre")}',
                'start': lanz.get('fecha_salida'),
                'backgroundColor': coleccion_color,
                'borderColor': coleccion_color,
                'extendedProps': {
                    'tipo': 'Lanzamiento',
                    'nombre': lanz.get('nombre'),
                    'juego': juego_nombre,
                    'coleccion': coleccion_nombre,
                    'juego_color': juego_color,
                    'coleccion_color': coleccion_color,
                    'precio': lanz.get('precio'),
                    'reserva': lanz.get('precio_reserva'),
                    'comentario': lanz.get('comentario'),
                    'fecha_envio': lanz.get('fecha_envio'),
                    'fecha_salida': lanz.get('fecha_salida')
                }
            })
            if lanz.get('fecha_envio'):
                eventos_calendario.append({
                    'id': f"envio-{lanz.get('id')}",
                    'title': f'{juego_inicial_badge} 📦 {lanz.get("nombre")}',
                    'start': lanz.get('fecha_envio'),
                    'backgroundColor': coleccion_color,
                    'borderColor': coleccion_color,
                    'extendedProps': {
                        'tipo': 'Envío',
                        'nombre': lanz.get('nombre'),
                        'lanzamiento_id': lanz.get('id'),
                        'juego': juego_nombre,
                        'coleccion': coleccion_nombre,
                        'juego_color': juego_color,
                        'coleccion_color': coleccion_color,
                        'precio': lanz.get('precio'),
                        'reserva': lanz.get('precio_reserva'),
                        'comentario': lanz.get('comentario'),
                        'fecha_salida': lanz.get('fecha_salida'),
                        'fecha_envio': lanz.get('fecha_envio')
                    }
                })

        for ev in eventos_data:
            juego_nombre = ev.get('juego')
            coleccion_nombre = ev.get('coleccion')
            juego_info = juegos_data.get(juego_nombre, {})
            juego_color = juego_info.get('color', '#6c757d')
            
            colecciones = juego_info.get('colecciones', [])
            coleccion_color = juego_color
            if coleccion_nombre and coleccion_nombre in colecciones:
                try:
                    idx = colecciones.index(coleccion_nombre)
                    factor = 1 - ((idx + 1) * 0.1)
                    coleccion_color = adjust_color_brightness(juego_color, factor)
                except (ValueError, TypeError):
                    pass
            
            juego_inicial_badge = f'<span class="badge" style="background-color: {juego_color};">{juego_nombre[0] if juego_nombre else " "}</span>'

            eventos_calendario.append({
                'id': ev.get('id'),
                'title': f'{juego_inicial_badge} 🎲 {ev.get("nombre")}',
                'start': ev.get('fecha'),
                'backgroundColor': coleccion_color,
                'borderColor': coleccion_color,
                'extendedProps': {
                    'tipo': 'Evento',
                    'nombre': ev.get('nombre'),
                    'juego': juego_nombre,
                    'coleccion': coleccion_nombre,
                    'juego_color': juego_color,
                    'coleccion_color': coleccion_color,
                    'precio': ev.get('precio'),
                    'reserva': ev.get('precio_reserva'),
                    'comentario': ev.get('comentario'),
                    'fecha': ev.get('fecha')
                }
            })

        return eventos_calendario, None

    except Exception as e:
        print(f"Error en obtener_eventos_calendario: {e}")
        return None, "No se pudieron cargar los eventos"
