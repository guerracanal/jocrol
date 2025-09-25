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
    
    pagado_monto = float(datos_reserva.get('pagado', 0) or 0)

    reserva = {
        "id": nuevo_id,
        "cliente_id": datos_reserva.get('cliente_id'),
        "lanzamiento_id": datos_reserva.get('producto_id') if datos_reserva.get('tipo_producto') == 'lanzamiento' else None,
        "evento_id": datos_reserva.get('producto_id') if datos_reserva.get('tipo_producto') == 'evento' else None,
        "cantidad": int(datos_reserva.get('cantidad') or 1),
        "fecha_reserva": datos_reserva.get('fecha_reserva') or datetime.now().strftime('%Y-%m-%d'),
        "estado": datos_reserva.get('estado', 'Pendiente'),
        "pagado": pagado_monto,
        "tipo_pago": datos_reserva.get('tipo_pago'),
        "notas": datos_reserva.get('notas'),
        "pago_completo": False
    }
    reservas.append(reserva)
    guardar_datos(RESERVAS_FILE, reservas)

def actualizar_reserva(reserva_id, datos_reserva):
    reservas = obtener_reservas_todas()
    reserva_actualizada = False
    for i, r in enumerate(reservas):
        if r.get('id') == reserva_id:
            reservas[i]['cliente_id'] = datos_reserva.get('cliente_id')
            
            tipo_producto = datos_reserva.get('tipo_producto')
            if tipo_producto == 'lanzamiento':
                reservas[i]['lanzamiento_id'] = datos_reserva.get('producto_id')
                reservas[i]['evento_id'] = None
            elif tipo_producto == 'evento':
                reservas[i]['evento_id'] = datos_reserva.get('producto_id')
                reservas[i]['lanzamiento_id'] = None
            
            reservas[i]['cantidad'] = int(datos_reserva.get('cantidad') or 1)
            reservas[i]['estado'] = datos_reserva.get('estado', r.get('estado'))
            
            pagado_val = datos_reserva.get('pagado')
            if pagado_val is not None and pagado_val != '':
                reservas[i]['pagado'] = float(pagado_val)
            else:
                reservas[i]['pagado'] = 0
            
            reservas[i]['tipo_pago'] = datos_reserva.get('tipo_pago')
            reservas[i]['notas'] = datos_reserva.get('notas')

            item_id = reservas[i].get('lanzamiento_id') or reservas[i].get('evento_id')
            item = None
            if reservas[i].get('lanzamiento_id'):
                item = next((l for l in obtener_lanzamientos_todos() if l['id'] == item_id), None)
            elif reservas[i].get('evento_id'):
                item = next((e for e in obtener_eventos_todos() if e['id'] == item_id), None)
            
            if item:
                precio = float(item.get('precio', 0))
                precio_reserva = float(item.get('precio_reserva', 0))
                cantidad = int(reservas[i]['cantidad'])
                total = (precio * cantidad) + precio_reserva
                reservas[i]['pago_completo'] = float(reservas[i]['pagado']) >= total

            reserva_actualizada = True
            break
    if not reserva_actualizada:
        raise ValueError(f"No se encontró la reserva con ID {reserva_id}")
    guardar_datos(RESERVAS_FILE, reservas)

def eliminar_reserva(reserva_id):
    reservas = obtener_reservas_todas()
    if not any(r['id'] == reserva_id for r in reservas):
        raise ValueError(f"No se encontró la reserva con ID {reserva_id}")
    
    reservas_actualizadas = [r for r in reservas if r['id'] != reserva_id]
    guardar_datos(RESERVAS_FILE, reservas_actualizadas)

def obtener_reservas_filtradas(filters):
    reservas_raw = obtener_reservas_todas()
    clientes = {c['id']: c for c in obtener_clientes_todos()}
    lanzamientos = {l['id']: l for l in obtener_lanzamientos_todos()}
    eventos = {e['id']: e for e in obtener_eventos_todos()}

    reservas_enriquecidas = []
    total_pendiente_general = 0

    for r in reservas_raw:
        item_id = r.get('lanzamiento_id') or r.get('evento_id')
        item = None
        if r.get('lanzamiento_id'):
            item = lanzamientos.get(item_id)
        elif r.get('evento_id'):
            item = eventos.get(item_id)

        cliente = clientes.get(r.get('cliente_id'))

        if not item or not cliente:
            continue

        r['item'] = item
        r['cliente'] = cliente

        precio = float(item.get('precio', 0))
        precio_reserva = float(item.get('precio_reserva', 0))
        cantidad = int(r.get('cantidad', 1))
        total = (precio * cantidad) + precio_reserva
        pagado = float(r.get('pagado', r.get('pagado_cantidad', 0)))
        pendiente = total - pagado

        r['total'] = total
        r['pendiente'] = pendiente
        r['pagado'] = pagado
        r['pago_completo'] = pagado >= total
        
        q = filters.get('q', '').lower()
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        payment_status = filters.get('payment_status')

        match = True
        if q and not (q in cliente['nombre'].lower() or q in item['nombre'].lower()):
            match = False
        if start_date and r.get('fecha_reserva') < start_date:
            match = False
        if end_date and r.get('fecha_reserva') > end_date:
            match = False
        if payment_status == 'pagado' and not r['pago_completo']:
            match = False
        if payment_status == 'pendiente' and r['pago_completo']:
            match = False
        
        if match:
            reservas_enriquecidas.append(r)
            if not r['pago_completo']:
                total_pendiente_general += pendiente

    return reservas_enriquecidas, total_pendiente_general
