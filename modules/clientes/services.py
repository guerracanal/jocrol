import uuid
from data.data_manager import CLIENTES_COLLECTION, RESERVAS_COLLECTION, LANZAMIENTOS_COLLECTION, EVENTOS_COLLECTION
from collections import defaultdict

def obtener_clientes_todos():
    return list(CLIENTES_COLLECTION.find({}, {'_id': 0}))

def obtener_cliente_por_id(cliente_id):
    return CLIENTES_COLLECTION.find_one({'id': cliente_id}, {'_id': 0})

def obtener_reservas_todas():
    return list(RESERVAS_COLLECTION.find({}, {'_id': 0}))

def obtener_lanzamientos_todos():
    return list(LANZAMIENTOS_COLLECTION.find({}, {'_id': 0}))

def obtener_eventos_todos():
    return list(EVENTOS_COLLECTION.find({}, {'_id': 0}))

def crear_cliente(nombre, email=None, telefono=None):
    if not nombre:
        raise ValueError("El nombre del cliente es obligatorio.")

    if email and CLIENTES_COLLECTION.find_one({'email': email}):
        raise ValueError(f"El email '{email}' ya está registrado.")

    nuevo_cliente = {
        'id': str(uuid.uuid4()),
        'nombre': nombre,
        'email': email,
        'telefono': telefono
    }

    CLIENTES_COLLECTION.insert_one(nuevo_cliente)
    # Quitar el _id de pymongo para que el resto de la app no se rompa
    del nuevo_cliente['_id']
    return nuevo_cliente

def actualizar_cliente(cliente_id, nombre, email=None, telefono=None):
    if not nombre:
        raise ValueError("El nombre del cliente es obligatorio.")

    if email:
        existing_client = CLIENTES_COLLECTION.find_one({'email': email})
        if existing_client and existing_client.get('id') != cliente_id:
            raise ValueError(f"El email '{email}' ya está registrado por otro cliente.")

    update_data = {
        '$set': {
            'nombre': nombre,
            'email': email,
            'telefono': telefono
        }
    }

    result = CLIENTES_COLLECTION.update_one({'id': cliente_id}, update_data)
    
    if result.matched_count == 0:
        raise ValueError(f"No se encontró el cliente con ID {cliente_id}")

def eliminar_cliente(cliente_id):
    if RESERVAS_COLLECTION.find_one({'cliente_id': cliente_id}):
        raise ValueError("No se puede eliminar un cliente que tiene reservas asociadas.")

    result = CLIENTES_COLLECTION.delete_one({'id': cliente_id})
    
    if result.deleted_count == 0:
        raise ValueError(f"No se encontró el cliente con ID {cliente_id}")

def obtener_clientes_con_reservas(q_filter=None):
    pipeline = []
    if q_filter:
        q = q_filter.lower()
        pipeline.append({
            '$match': {
                '$or': [
                    {'nombre': {'$regex': q, '$options': 'i'}},
                    {'email': {'$regex': q, '$options': 'i'}},
                    {'telefono': {'$regex': q, '$options': 'i'}}
                ]
            }
        })
    
    # Proyectar para excluir _id
    pipeline.append({'$project': {'_id': 0}})

    clientes_filtrados = list(CLIENTES_COLLECTION.aggregate(pipeline))
    cliente_ids = [c['id'] for c in clientes_filtrados]

    reservas_por_cliente = defaultdict(list)
    lanzamiento_ids = set()
    evento_ids = set()

    if cliente_ids:
        reservas_cursor = RESERVAS_COLLECTION.find({'cliente_id': {'$in': cliente_ids}}, {'_id': 0})
        for res in reservas_cursor:
            reservas_por_cliente[res['cliente_id']].append(res)
            if res.get('lanzamiento_id'):
                lanzamiento_ids.add(res.get('lanzamiento_id'))
            if res.get('evento_id'):
                evento_ids.add(res.get('evento_id'))

    lanzamientos = {l['id']: l for l in LANZAMIENTOS_COLLECTION.find({'id': {'$in': list(lanzamiento_ids)}}, {'_id': 0})}
    eventos = {e['id']: e for e in EVENTOS_COLLECTION.find({'id': {'$in': list(evento_ids)}}, {'_id': 0})}

    for cliente in clientes_filtrados:
        reservas_cliente = reservas_por_cliente.get(cliente['id'], [])
        for res in reservas_cliente:
            item = None
            if res.get('lanzamiento_id'):
                item = lanzamientos.get(res.get('lanzamiento_id'))
            elif res.get('evento_id'):
                item = eventos.get(res.get('evento_id'))
            res['item'] = item
        cliente['reservas'] = reservas_cliente

    return clientes_filtrados

