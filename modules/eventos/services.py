from data.data_manager import cargar_datos, guardar_datos, EVENTOS_FILE
import uuid

def generar_id():
    return str(uuid.uuid4())

def obtener_eventos_todos():
    return cargar_datos(EVENTOS_FILE)

def obtener_evento_por_id(evento_id):
    eventos = obtener_eventos_todos()
    for e in eventos:
        if e.get('id') == evento_id:
            return e
    return None

def crear_evento(datos_evento):
    eventos = obtener_eventos_todos()
    nuevo_id = generar_id()
    evento = {
        "id": nuevo_id,
        "nombre": datos_evento.get('nombre'),
        "coleccion": "EVENTOS",
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
            eventos[i]['nombre'] = datos_evento.get('nombre', e.get('nombre'))
            eventos[i]['fecha_salida'] = datos_evento.get('fecha_salida', e.get('fecha_salida'))
            eventos[i]['precio'] = float(datos_evento.get('precio', e.get('precio')) or 0)
            eventos[i]['reserva'] = float(datos_evento.get('reserva', e.get('reserva')) or 0)
            eventos[i]['comentario'] = datos_evento.get('comentario', e.get('comentario'))
            eventos[i]['fecha'] = datos_evento.get('fecha_salida', e.get('fecha_salida'))
            break
    guardar_datos(EVENTOS_FILE, eventos)
