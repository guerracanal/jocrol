from data.data_manager import RESERVAS_COLLECTION, CLIENTES_COLLECTION, LANZAMIENTOS_COLLECTION, EVENTOS_COLLECTION
from datetime import datetime
import uuid
from bson.objectid import ObjectId

def generar_id():
    return str(uuid.uuid4())

def obtener_reservas_todas():
    return list(RESERVAS_COLLECTION.find({}, {'_id': 0}))

def obtener_clientes_todos():
    return list(CLIENTES_COLLECTION.find({}, {'_id': 0}))

def obtener_lanzamientos_todos():
    return list(LANZAMIENTOS_COLLECTION.find({}, {'_id': 0}))

def obtener_eventos_todos():
    return list(EVENTOS_COLLECTION.find({}, {'_id': 0}))

def obtener_reserva_por_id(reserva_id):
    return RESERVAS_COLLECTION.find_one({'id': reserva_id}, {'_id': 0})

def crear_reserva(datos_reserva):
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
    RESERVAS_COLLECTION.insert_one(reserva)

def actualizar_reserva(reserva_id, datos_reserva):
    update_fields = {
        'cliente_id': datos_reserva.get('cliente_id'),
        'cantidad': int(datos_reserva.get('cantidad') or 1),
        'estado': datos_reserva.get('estado'),
        'tipo_pago': datos_reserva.get('tipo_pago'),
        'notas': datos_reserva.get('notas')
    }

    tipo_producto = datos_reserva.get('tipo_producto')
    if tipo_producto == 'lanzamiento':
        update_fields['lanzamiento_id'] = datos_reserva.get('producto_id')
        update_fields['evento_id'] = None
    elif tipo_producto == 'evento':
        update_fields['evento_id'] = datos_reserva.get('producto_id')
        update_fields['lanzamiento_id'] = None

    pagado_val = datos_reserva.get('pagado')
    if pagado_val is not None and pagado_val != '':
        update_fields['pagado'] = float(pagado_val)
    else:
        update_fields['pagado'] = 0

    reserva_actual = RESERVAS_COLLECTION.find_one({'id': reserva_id})
    if not reserva_actual:
        raise ValueError(f"No se encontró la reserva con ID {reserva_id}")

    item_id = update_fields.get('lanzamiento_id') or update_fields.get('evento_id')
    item = None
    if update_fields.get('lanzamiento_id'):
        item = LANZAMIENTOS_COLLECTION.find_one({'id': item_id})
    elif update_fields.get('evento_id'):
        item = EVENTOS_COLLECTION.find_one({'id': item_id})
    
    if item:
        precio = float(item.get('precio', 0))
        precio_reserva = float(item.get('precio_reserva', 0))
        cantidad = int(update_fields['cantidad'])
        total = (precio * cantidad) + precio_reserva
        update_fields['pago_completo'] = float(update_fields['pagado']) >= total

    result = RESERVAS_COLLECTION.update_one({'id': reserva_id}, {'$set': update_fields})
    if result.matched_count == 0:
        raise ValueError(f"No se encontró la reserva con ID {reserva_id}")

def eliminar_reserva(reserva_id):
    result = RESERVAS_COLLECTION.delete_one({'id': reserva_id})
    if result.deleted_count == 0:
        raise ValueError(f"No se encontró la reserva con ID {reserva_id}")

def obtener_reservas_filtradas(filters):
    pipeline = []

    # Match stage for filtering
    match_stage = {}
    q = filters.get('q', '').lower()
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    
    if start_date:
        match_stage['fecha_reserva'] = {'$gte': start_date}
    if end_date:
        if 'fecha_reserva' in match_stage:
            match_stage['fecha_reserva']['$lte'] = end_date
        else:
            match_stage['fecha_reserva'] = {'$lte': end_date}

    if match_stage:
        pipeline.append({'$match': match_stage})

    # Lookup stage for cliente
    pipeline.append({
        '$lookup': {
            'from': 'clientes',
            'localField': 'cliente_id',
            'foreignField': 'id',
            'as': 'cliente'
        }
    })
    pipeline.append({'$unwind': '$cliente'})

    # Lookup stage for lanzamientos
    pipeline.append({
        '$lookup': {
            'from': 'lanzamientos',
            'localField': 'lanzamiento_id',
            'foreignField': 'id',
            'as': 'lanzamiento_item'
        }
    })
    
    # Lookup stage for eventos
    pipeline.append({
        '$lookup': {
            'from': 'eventos',
            'localField': 'evento_id',
            'foreignField': 'id',
            'as': 'evento_item'
        }
    })

    # Add fields for item
    pipeline.append({
        '$addFields': {
            'item': {
                '$cond': {
                    'if': {'$gt': [{'$size': '$lanzamiento_item'}, 0]},
                    'then': {'$arrayElemAt': ['$lanzamiento_item', 0]},
                    'else': {'$arrayElemAt': ['$evento_item', 0]}
                }
            }
        }
    })

    # Filter by query on cliente and item name
    if q:
        pipeline.append({
            '$match': {
                '$or': [
                    {'cliente.nombre': {'$regex': q, '$options': 'i'}},
                    {'item.nombre': {'$regex': q, '$options': 'i'}}
                ]
            }
        })
    
    # Add fields for total, pendiente, pagado, and pago_completo
    pipeline.append({
        '$addFields': {
            'total': {
                '$add': [
                    {'$multiply': [{'$toDouble': '$item.precio'}, {'$toInt': '$cantidad'}]},
                    {'$toDouble': '$item.precio_reserva'}
                ]
            },
            'pagado': {'$toDouble': '$pagado'}
        }
    })
    pipeline.append({
        '$addFields': {
            'pendiente': {'$subtract': ['$total', '$pagado']},
            'pago_completo': {'$gte': ['$pagado', '$total']}
        }
    })

    # Filter by payment_status
    payment_status = filters.get('payment_status')
    if payment_status == 'pagado':
        pipeline.append({'$match': {'pago_completo': True}})
    elif payment_status == 'pendiente':
        pipeline.append({'$match': {'pago_completo': False}})
        
    # Projection to remove temp fields
    pipeline.append({'$project': {'lanzamiento_item': 0, 'evento_item': 0, '_id':0}})

    reservas_enriquecidas = list(RESERVAS_COLLECTION.aggregate(pipeline))

    total_pendiente_general = sum(r['pendiente'] for r in reservas_enriquecidas if not r['pago_completo'])

    return reservas_enriquecidas, total_pendiente_general
