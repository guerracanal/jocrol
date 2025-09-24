from data.data_manager import cargar_datos, LANZAMIENTOS_FILE, EVENTOS_FILE, COLECCIONES_FILE

def obtener_eventos_calendario():
    try:
        lanzamientos = cargar_datos(LANZAMIENTOS_FILE)
        eventos_data = cargar_datos(EVENTOS_FILE)
        colecciones = {c['nombre']: c for c in cargar_datos(COLECCIONES_FILE)}

        eventos_calendario = []

        for lanz in lanzamientos:
            color = colecciones.get(lanz.get('coleccion'), {}).get('color', '#0d6efd')
            eventos_calendario.append({
                'id': f"salida-{lanz.get('id')}",
                'title': f"🚀 {lanz.get('nombre')}",
                'start': lanz.get('fecha_salida'),
                'backgroundColor': color,
                'borderColor': color,
                'extendedProps': {
                    'tipo': 'Lanzamiento',
                    'coleccion': lanz.get('coleccion'),
                    'precio': lanz.get('precio'),
                    'reserva': lanz.get('reserva'),
                    'comentario': lanz.get('comentario'),
                    'fecha_envio': lanz.get('fecha_envio'),
                    'fecha_salida': lanz.get('fecha_salida'),
                    'color': color
                }
            })
            if lanz.get('fecha_envio'):
                eventos_calendario.append({
                    'id': f"envio-{lanz.get('id')}",
                    'title': f"📦 {lanz.get('nombre')}",
                    'start': lanz.get('fecha_envio'),
                    'backgroundColor': color,
                    'borderColor': color,
                    'extendedProps': {
                        'tipo': 'Envío',
                        'lanzamiento_id': lanz.get('id'),
                        'coleccion': lanz.get('coleccion'),
                        'precio': lanz.get('precio'),
                        'reserva': lanz.get('reserva'),
                        'comentario': lanz.get('comentario'),
                        'fecha_salida': lanz.get('fecha_salida'),
                        'fecha_envio': lanz.get('fecha_envio'),
                        'color': color
                    }
                })

        for ev in eventos_data:
            color = colecciones.get(ev.get('coleccion'), {}).get('color', '#6c757d')
            eventos_calendario.append({
                'id': ev.get('id'),
                'title': f"🎲 {ev.get('nombre')}",
                'start': ev.get('fecha'),
                'backgroundColor': color,
                'borderColor': color,
                'extendedProps': {
                    'tipo': 'Evento',
                    'coleccion': ev.get('coleccion'),
                    'precio': ev.get('precio'),
                    'reserva': ev.get('reserva'),
                    'comentario': ev.get('comentario'),
                    'color': color,
                }
            })

        return eventos_calendario, None

    except Exception as e:
        print(f"Error en obtener_eventos_calendario: {e}")
        return None, "No se pudieron cargar los eventos"
