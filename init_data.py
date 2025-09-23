import json
import os
import uuid
from datetime import datetime, timedelta

# Crear directorio de datos
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def generar_id():
    return str(uuid.uuid4())

# Datos de ejemplo para lanzamientos
lanzamientos = [
    {
        'id': generar_id(),
        'nombre': 'Cajas de sobres',
        'coleccion': "Marvel's Spiderman",
        'fecha_salida': '2025-09-26',
        'precio': 195.00,
        'reserva': 20.00,
        'tipo': 'Cajas de sobres'
    },
    {
        'id': generar_id(),
        'nombre': 'Bundle',
        'coleccion': "Marvel's Spiderman",
        'fecha_salida': '2025-09-26',
        'precio': 70.00,
        'reserva': 5.00,
        'tipo': 'Bundle'
    },
    {
        'id': generar_id(),
        'nombre': 'Caja de escena',
        'coleccion': "Marvel's Spiderman",
        'fecha_salida': '2025-09-26',
        'precio': 45.00,
        'reserva': 5.00,
        'tipo': 'Caja de escena'
    },
    {
        'id': generar_id(),
        'nombre': 'Comm Party 1',
        'coleccion': 'EVENTOS',
        'fecha_salida': '2025-10-04',
        'precio': 0.00,
        'reserva': 0.00,
        'tipo': 'Evento'
    },
    {
        'id': generar_id(),
        'nombre': 'Halloween Spiderman',
        'coleccion': 'EVENTOS',
        'fecha_salida': '2025-10-31',
        'precio': 0.00,
        'reserva': 0.00,
        'tipo': 'Evento'
    },
    {
        'id': generar_id(),
        'nombre': 'Cajas de sobres',
        'coleccion': 'Avatar',
        'fecha_salida': '2025-11-21',
        'precio': 195.00,
        'reserva': 20.00,
        'tipo': 'Cajas de sobres'
    }
]

# Datos de ejemplo para clientes
clientes = [
    {
        'id': generar_id(),
        'nombre': 'Juan Pérez',
        'email': 'juan@email.com',
        'telefono': '666777888',
        'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'id': generar_id(),
        'nombre': 'María García',
        'email': 'maria@email.com',
        'telefono': '666111222',
        'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    },
    {
        'id': generar_id(),
        'nombre': 'Carlos López',
        'email': 'carlos@email.com',
        'telefono': '666333444',
        'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
]

# Datos de ejemplo para reservas
reservas = [
    {
        'id': generar_id(),
        'lanzamiento_id': lanzamientos[0]['id'],  # Cajas de sobres Spiderman
        'cliente_id': clientes[0]['id'],  # Juan
        'cantidad': 1,
        'fecha_reserva': '2025-09-23',
        'pagado': True,
        'notas': '295 puntos de fidelidad aplicados',
        'estado': 'confirmada'
    },
    {
        'id': generar_id(),
        'lanzamiento_id': lanzamientos[1]['id'],  # Bundle Spiderman
        'cliente_id': clientes[1]['id'],  # María
        'cantidad': 2,
        'fecha_reserva': '2025-09-23',
        'pagado': False,
        'notas': 'Pendiente de pago. Contactar esta semana.',
        'estado': 'pendiente'
    },
    {
        'id': generar_id(),
        'lanzamiento_id': lanzamientos[5]['id'],  # Cajas de sobres Avatar
        'cliente_id': clientes[2]['id'],  # Carlos
        'cantidad': 1,
        'fecha_reserva': '2025-09-23',
        'pagado': False,
        'notas': '',
        'estado': 'pendiente'
    }
]

# Guardar datos en archivos JSON
with open(os.path.join(DATA_DIR, 'lanzamientos.json'), 'w', encoding='utf-8') as f:
    json.dump(lanzamientos, f, ensure_ascii=False, indent=2)

with open(os.path.join(DATA_DIR, 'clientes.json'), 'w', encoding='utf-8') as f:
    json.dump(clientes, f, ensure_ascii=False, indent=2)

with open(os.path.join(DATA_DIR, 'reservas.json'), 'w', encoding='utf-8') as f:
    json.dump(reservas, f, ensure_ascii=False, indent=2)

print("Datos de ejemplo creados exitosamente:")
print(f"- {len(lanzamientos)} lanzamientos")
print(f"- {len(clientes)} clientes") 
print(f"- {len(reservas)} reservas")
print("\nPuedes ejecutar la aplicación con: python app.py")