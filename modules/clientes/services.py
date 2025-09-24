import uuid
from data.data_manager import cargar_datos, guardar_datos, CLIENTES_FILE, RESERVAS_FILE, LANZAMIENTOS_FILE, EVENTOS_FILE
from collections import defaultdict

def obtener_clientes_todos():
    return cargar_datos(CLIENTES_FILE)

def obtener_cliente_por_id(cliente_id):
    clientes = obtener_clientes_todos()
    for c in clientes:
        if c.get('id') == cliente_id:
            return c
    return None

def obtener_reservas_todas():
    return cargar_datos(RESERVAS_FILE)

def obtener_lanzamientos_todos():
    return cargar_datos(LANZAMIENTOS_FILE)

def obtener_eventos_todos():
    return cargar_datos(EVENTOS_FILE)

def crear_cliente(nombre, email=None, telefono=None):
    if not nombre:
        raise ValueError("El nombre del cliente es obligatorio.")

    clientes = obtener_clientes_todos()

    if email and any(c.get('email') == email for c in clientes):
        raise ValueError(f"El email '{email}' ya está registrado.")

    nuevo_cliente = {
        'id': str(uuid.uuid4()),
        'nombre': nombre,
        'email': email,
        'telefono': telefono
    }

    clientes.append(nuevo_cliente)
    guardar_datos(CLIENTES_FILE, clientes)
    return nuevo_cliente

def actualizar_cliente(cliente_id, nombre, email=None, telefono=None):
    if not nombre:
        raise ValueError("El nombre del cliente es obligatorio.")

    clientes = obtener_clientes_todos()

    if email:
        for c in clientes:
            if c.get('email') == email and c.get('id') != cliente_id:
                raise ValueError(f"El email '{email}' ya está registrado por otro cliente.")

    cliente_actualizado = False
    for i, c in enumerate(clientes):
        if c.get('id') == cliente_id:
            clientes[i]['nombre'] = nombre
            clientes[i]['email'] = email
            clientes[i]['telefono'] = telefono
            cliente_actualizado = True
            break
    
    if not cliente_actualizado:
        raise ValueError(f"No se encontró el cliente con ID {cliente_id}")

    guardar_datos(CLIENTES_FILE, clientes)

def eliminar_cliente(cliente_id):
    clientes = obtener_clientes_todos()
    reservas = obtener_reservas_todas()

    if any(r.get('cliente_id') == cliente_id for r in reservas):
        raise ValueError("No se puede eliminar un cliente que tiene reservas asociadas.")

    cliente_encontrado = False
    for i, c in enumerate(clientes):
        if c.get('id') == cliente_id:
            del clientes[i]
            cliente_encontrado = True
            break
    
    if not cliente_encontrado:
        raise ValueError(f"No se encontró el cliente con ID {cliente_id}")

    guardar_datos(CLIENTES_FILE, clientes)

def obtener_clientes_con_reservas(q_filter=None):
    clientes_todos = obtener_clientes_todos()
    reservas = obtener_reservas_todas()
    lanzamientos = {l['id']: l for l in obtener_lanzamientos_todos()}
    eventos = {e['id']: e for e in obtener_eventos_todos()}

    clientes_filtrados = clientes_todos
    if q_filter:
        q = q_filter.lower()
        clientes_filtrados = [
            c for c in clientes_filtrados
            if q in c.get('nombre', '').lower() or 
               q in c.get('email', '').lower() or 
               q in c.get('telefono', '').lower()
        ]

    reservas_por_cliente = defaultdict(list)
    for res in reservas:
        item = None
        if res.get('tipo_reserva') == 'lanzamiento':
            item = lanzamientos.get(res.get('lanzamiento_id'))
        elif res.get('tipo_reserva') == 'evento':
            item = eventos.get(res.get('evento_id'))
        res['item'] = item
        reservas_por_cliente[res.get('cliente_id')].append(res)

    for cliente in clientes_filtrados:
        cliente['reservas'] = reservas_por_cliente.get(cliente.get('id'), [])

    return clientes_filtrados
