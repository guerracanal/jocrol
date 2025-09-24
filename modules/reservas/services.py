from data.data_manager import cargar_datos, guardar_datos, RESERVAS_FILE, CLIENTES_FILE, LANZAMIENTOS_FILE, EVENTOS_FILE
from datetime import datetime
import uuid

def generar_id():
    return str(uuid.uuid4())

def obtener_reservas_todas():
    return cargar_datos(RESERVAS_FILE)

def obtener_clientes_todos():
    return cargar_datos(CLIENTES_FILE)

def obtener_lanzamientos_todos():
    return cargar_datos(LANZAMIENTOS_FILE)

def obtener_eventos_todos():
    return cargar_datos(EVENTOS_FILE)

def obtener_reserva_por_id(reserva_id):
    reservas = obtener_reservas_todas()
    for r in reservas:
        if r.get('id') == reserva_id:
            return r
    return None

def crear_reserva(datos_reserva):
    reservas = obtener_reservas_todas()
    nuevo_id = generar_id()
    reserva = {
        "id": nuevo_id,
        "cliente_id": datos_reserva.get('cliente_id'),
        "tipo_reserva": datos_reserva.get('tipo_reserva'),
        "lanzamiento_id": datos_reserva.get('lanzamiento_id') if datos_reserva.get('tipo_reserva') == 'lanzamiento' else None,
        "evento_id": datos_reserva.get('evento_id') if datos_reserva.get('tipo_reserva') == 'evento' else None,
        "cantidad": int(datos_reserva.get('cantidad') or 1),
        "fecha_reserva": datos_reserva.get('fecha_reserva') or datetime.now().strftime('%Y-%m-%d'),
        "estado": datos_reserva.get('estado', 'pendiente'),
        "pagado": 'pagado' in datos_reserva,
        "pagado_cantidad": float(datos_reserva.get('pagado_cantidad') or 0),
        "tipo_pago": datos_reserva.get('tipo_pago'),
        "notas": datos_reserva.get('notas')
    }
    reservas.append(reserva)
    guardar_datos(RESERVAS_FILE, reservas)

def actualizar_reserva(reserva_id, datos_reserva):
    reservas = obtener_reservas_todas()
    reserva_actualizada = False
    for i, r in enumerate(reservas):
        if r.get('id') == reserva_id:
            reservas[i]['cliente_id'] = datos_reserva.get('cliente_id')
            reservas[i]['tipo_reserva'] = datos_reserva.get('tipo_reserva')
            reservas[i]['lanzamiento_id'] = datos_reserva.get('lanzamiento_id') if datos_reserva.get('tipo_reserva') == 'lanzamiento' else None
            reservas[i]['evento_id'] = datos_reserva.get('evento_id') if datos_reserva.get('tipo_reserva') == 'evento' else None
            reservas[i]['cantidad'] = int(datos_reserva.get('cantidad') or 1)
            reservas[i]['fecha_reserva'] = datos_reserva.get('fecha_reserva', r.get('fecha_reserva'))
            reservas[i]['estado'] = datos_reserva.get('estado', r.get('estado'))
            reservas[i]['pagado'] = 'pagado' in datos_reserva
            reservas[i]['pagado_cantidad'] = float(datos_reserva.get('pagado_cantidad') or 0)
            reservas[i]['tipo_pago'] = datos_reserva.get('tipo_pago')
            reservas[i]['notas'] = datos_reserva.get('notas')
            reserva_actualizada = True
            break
    if not reserva_actualizada:
        raise ValueError(f"No se encontró la reserva con ID {reserva_id}")
    guardar_datos(RESERVAS_FILE, reservas)

def eliminar_reserva(reserva_id):
    reservas = obtener_reservas_todas()
    reserva_encontrada = False
    for i, r in enumerate(reservas):
        if r.get('id') == reserva_id:
            del reservas[i]
            reserva_encontrada = True
            break
    if not reserva_encontrada:
        raise ValueError(f"No se encontró la reserva con ID {reserva_id}")
    guardar_datos(RESERVAS_FILE, reservas)

def obtener_reservas_filtradas(filters):
    reservas_raw = obtener_reservas_todas()
    clientes = {c['id']: c for c in obtener_clientes_todos()}
    lanzamientos = {l['id']: l for l in obtener_lanzamientos_todos()}
    eventos = {e['id']: e for e in obtener_eventos_todos()}

    reservas_enriquecidas = []
    for r in reservas_raw:
        r['cliente'] = clientes.get(r.get('cliente_id'))
        if r.get('tipo_reserva') == 'lanzamiento':
            r['item'] = lanzamientos.get(r.get('lanzamiento_id'))
        elif r.get('tipo_reserva') == 'evento':
            r['item'] = eventos.get(r.get('evento_id'))
        else:
            r['item'] = None
        reservas_enriquecidas.append(r)

    reservas_filtradas = reservas_enriquecidas

    if filters.get('q'):
        q = filters['q'].lower()
        reservas_filtradas = [
            r for r in reservas_filtradas if
            (r['cliente'] and q in r['cliente'].get('nombre', '').lower()) or
            (r['item'] and q in r['item'].get('nombre', '').lower())
        ]

    if filters.get('start_date'):
        reservas_filtradas = [r for r in reservas_filtradas if r.get('fecha_reserva') >= filters['start_date']]

    if filters.get('end_date'):
        reservas_filtradas = [r for r in reservas_filtradas if r.get('fecha_reserva') <= filters['end_date']]

    if filters.get('payment_status'):
        if filters['payment_status'] == 'pagado':
            reservas_filtradas = [r for r in reservas_filtradas if r.get('pagado')]
        elif filters['payment_status'] == 'pendiente':
            reservas_filtradas = [r for r in reservas_filtradas if not r.get('pagado')]

    reservas_procesadas = []
    total_pendiente = 0

    for r in reservas_filtradas:
        item = r['item']
        precio_total = 0
        if item:
            precio_item = float(item.get('precio', 0))
            cantidad = int(r.get('cantidad', 0))
            precio_total = precio_item * cantidad

        pagado_cantidad = float(r.get('pagado_cantidad', 0))
        r['pagado_cantidad'] = pagado_cantidad
        r['pendiente'] = precio_total - pagado_cantidad
        total_pendiente += r['pendiente']
        reservas_procesadas.append(r)

    return reservas_procesadas, total_pendiente
