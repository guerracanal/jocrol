from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
from datetime import datetime
import uuid
import random
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# --- CONFIGURACIÓN DE COLORES ---
BOOTSTRAP_COLORS = ['#0d6efd', '#6f42c1', '#d63384', '#dc3545', '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0']

# --- FILTROS DE PLANTILLAS ---
@app.template_filter('formato_fecha')
def format_date(value, format='%d/%m/%Y'):
    if not value: return ""
    try:
        date_obj = datetime.strptime(value.split(' ')[0], '%Y-%m-%d')
        return date_obj.strftime(format)
    except (ValueError, TypeError): return value

@app.template_filter('formato_fecha_hora')
def format_datetime(value, format='%d/%m/%Y %H:%M'):
    if not value:
        return ""
    try:
        date_obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return date_obj.strftime(format)
    except (ValueError, TypeError):
        return value

# --- RUTAS DE ARCHIVOS ---
DATA_DIR = 'data'
LANZAMIENTOS_FILE = os.path.join(DATA_DIR, 'lanzamientos.json')
CLIENTES_FILE = os.path.join(DATA_DIR, 'clientes.json')
RESERVAS_FILE = os.path.join(DATA_DIR, 'reservas.json')
COLECCIONES_FILE = os.path.join(DATA_DIR, 'colecciones.json')
EVENTOS_FILE = os.path.join(DATA_DIR, 'eventos.json')
RECORDATORIOS_FILE = os.path.join(DATA_DIR, 'recordatorios.json')
STAFF_FILE = os.path.join(DATA_DIR, 'staff.json')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- FUNCIONES DE MANEJO DE DATOS ---
def cargar_datos(archivo):
    if not os.path.exists(archivo): return []
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError): return []

def guardar_datos(archivo, datos):
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def generar_id(): return str(uuid.uuid4())

# --- RUTAS PRINCIPALES Y DE API ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calendario')
def calendario():
    staff = cargar_datos(STAFF_FILE)
    return render_template('calendario.html', staff=staff)

@app.route('/api/eventos')
def api_eventos():
    try:
        lanzamientos = cargar_datos(LANZAMIENTOS_FILE)
        eventos_data = cargar_datos(EVENTOS_FILE)
        recordatorios_data = cargar_datos(RECORDATORIOS_FILE)
        colecciones = {c['nombre']: c['color'] for c in cargar_datos(COLECCIONES_FILE)}

        eventos_calendario = []

        for lanz in lanzamientos:
            color = colecciones.get(lanz.get('coleccion'), '#0d6efd')
            eventos_calendario.append({
                'id': f"salida-{lanz.get('id')}",
                'title': lanz.get('nombre'),
                'start': lanz.get('fecha_salida'),
                'backgroundColor': color,
                'borderColor': color,
                'extendedProps': {'tipo': 'lanzamiento'}
            })
            if lanz.get('fecha_envio'):
                eventos_calendario.append({
                    'id': f"envio-{lanz.get('id')}",
                    'title': f"Envío: {lanz.get('nombre')}",
                    'start': lanz.get('fecha_envio'),
                    'backgroundColor': '#198754',
                    'borderColor': '#198754',
                    'extendedProps': {'tipo': 'envio'}
                })

        for ev in eventos_data:
            eventos_calendario.append({
                'id': ev.get('id'),
                'title': ev.get('nombre'),
                'start': ev.get('fecha'),
                'backgroundColor': '#6c757d',
                'borderColor': '#6c757d',
                'extendedProps': { 'tipo': 'evento' }
            })

        for rec in recordatorios_data:
            eventos_calendario.append({
                'id': rec.get('id'),
                'title': f"Recordatorio: {rec.get('titulo')}",
                'start': rec.get('fecha'),
                'backgroundColor': '#fd7e14',
                'borderColor': '#fd7e14',
                'extendedProps': { 'tipo': 'recordatorio' }
            })

        return jsonify(eventos_calendario)

    except Exception as e:
        print(f"Error en /api/eventos: {e}")
        return jsonify({"error": "No se pudieron cargar los eventos"}), 500

# --- GESTIÓN DE LANZAMIENTOS ---
@app.route('/lanzamientos')
def listar_lanzamientos():
    lanzamientos_todos = cargar_datos(LANZAMIENTOS_FILE)
    reservas = cargar_datos(RESERVAS_FILE)
    clientes = {c['id']: c for c in cargar_datos(CLIENTES_FILE)}
    colecciones = {c['nombre']: c for c in cargar_datos(COLECCIONES_FILE)}
    
    filters = {
        'q': request.args.get('q', ''),
        'start_date': request.args.get('start_date', ''),
        'end_date': request.args.get('end_date', ''),
        'hide_past': request.args.get('hide_past', 'off')
    }
    
    lanzamientos_filtrados = lanzamientos_todos

    if filters['q']:
        q = filters['q'].lower()
        lanzamientos_filtrados = [
            l for l in lanzamientos_filtrados 
            if q in l.get('nombre', '').lower() or q in l.get('coleccion', '').lower()
        ]

    if filters['start_date']:
        lanzamientos_filtrados = [l for l in lanzamientos_filtrados if l.get('fecha_salida') >= filters['start_date']]

    if filters['end_date']:
        lanzamientos_filtrados = [l for l in lanzamientos_filtrados if l.get('fecha_salida') <= filters['end_date']]

    if filters['hide_past'] == 'on':
        today = datetime.now().strftime('%Y-%m-%d')
        lanzamientos_filtrados = [l for l in lanzamientos_filtrados if l.get('fecha_salida') >= today]

    reservas_por_lanzamiento = defaultdict(list)
    for res in reservas:
        res['cliente'] = clientes.get(res.get('cliente_id'))
        reservas_por_lanzamiento[res.get('lanzamiento_id')].append(res)

    for lanz in lanzamientos_filtrados:
        lanz['reservas'] = reservas_por_lanzamiento.get(lanz.get('id'), [])
        lanz['coleccion_data'] = colecciones.get(lanz.get('coleccion'))

    return render_template('lanzamientos.html', lanzamientos=lanzamientos_filtrados, colecciones=colecciones.values(), filters=filters)

@app.route('/lanzamientos/nuevo', methods=['GET', 'POST'])
def nuevo_lanzamiento():
    flash('Funcionalidad "Añadir Lanzamiento" no implementada.', 'warning')
    return redirect(url_for('listar_lanzamientos'))

@app.route('/lanzamientos/editar/<lanzamiento_id>', methods=['GET', 'POST'])
def editar_lanzamiento(lanzamiento_id):
    flash(f'Funcionalidad "Editar Lanzamiento {lanzamiento_id}" no implementada.', 'warning')
    return redirect(url_for('listar_lanzamientos'))

@app.route('/lanzamientos/eliminar/<lanzamiento_id>')
def eliminar_lanzamiento(lanzamiento_id):
    flash(f'Funcionalidad "Eliminar Lanzamiento {lanzamiento_id}" no implementada.', 'warning')
    return redirect(url_for('listar_lanzamientos'))

# --- GESTIÓN DE EVENTOS ---
@app.route('/eventos')
def listar_eventos():
    eventos = cargar_datos(EVENTOS_FILE)
    return render_template('eventos.html', eventos=eventos, filters={})

@app.route('/eventos/nuevo', methods=['GET', 'POST'])
def nuevo_evento():
    flash('Funcionalidad "Añadir Evento" no implementada.', 'warning')
    return redirect(url_for('listar_eventos'))

@app.route('/eventos/eliminar/<evento_id>')
def eliminar_evento(evento_id):
    flash(f'Funcionalidad "Eliminar Evento {evento_id}" no implementada.', 'warning')
    return redirect(url_for('listar_eventos'))

# --- GESTIÓN DE RESERVAS ---
@app.route('/reservas')
def listar_reservas():
    reservas_raw = cargar_datos(RESERVAS_FILE)
    clientes = {c['id']: c for c in cargar_datos(CLIENTES_FILE)}
    lanzamientos = {l['id']: l for l in cargar_datos(LANZAMIENTOS_FILE)}
    
    reservas_procesadas = []
    total_pendiente = 0

    for r in reservas_raw:
        lanzamiento = lanzamientos.get(r.get('lanzamiento_id'))
        precio_total = 0
        if lanzamiento:
            precio_lanzamiento = float(lanzamiento.get('precio', 0))
            cantidad = int(r.get('cantidad', 0))
            precio_total = precio_lanzamiento * cantidad

        pagado_cantidad = float(r.get('pagado_cantidad', 0))
        r['pagado_cantidad'] = pagado_cantidad
        r['cliente'] = clientes.get(r.get('cliente_id'))
        r['lanzamiento'] = lanzamiento
        r['pendiente'] = precio_total - pagado_cantidad
        total_pendiente += r['pendiente']
        reservas_procesadas.append(r)

    return render_template('reservas.html', reservas=reservas_procesadas, total_pendiente=total_pendiente, filters={})

@app.route('/reservas/nueva', methods=['GET', 'POST'])
def nueva_reserva():
    flash('Funcionalidad "Añadir Reserva" no implementada.', 'warning')
    return redirect(url_for('listar_reservas'))

@app.route('/reservas/editar/<reserva_id>', methods=['GET', 'POST'])
def editar_reserva(reserva_id):
    flash(f'Funcionalidad "Editar Reserva {reserva_id}" no implementada.', 'warning')
    return redirect(url_for('listar_reservas'))

@app.route('/reservas/eliminar/<reserva_id>')
def eliminar_reserva(reserva_id):
    flash(f'Funcionalidad "Eliminar Reserva {reserva_id}" no implementada.', 'warning')
    return redirect(url_for('listar_reservas'))

# --- GESTIÓN DE CLIENTES ---
@app.route('/clientes')
def listar_clientes():
    clientes_todos = cargar_datos(CLIENTES_FILE)
    reservas = cargar_datos(RESERVAS_FILE)
    lanzamientos = {l['id']: l for l in cargar_datos(LANZAMIENTOS_FILE)}

    reservas_por_cliente = defaultdict(list)
    for res in reservas:
        res['lanzamiento'] = lanzamientos.get(res.get('lanzamiento_id'))
        reservas_por_cliente[res.get('cliente_id')].append(res)

    for cliente in clientes_todos:
        cliente['reservas'] = reservas_por_cliente.get(cliente.get('id'), [])

    return render_template('clientes.html', clientes=clientes_todos, filters={})

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    flash('Funcionalidad "Añadir Cliente" no implementada.', 'warning')
    return redirect(url_for('listar_clientes'))

@app.route('/clientes/eliminar/<cliente_id>')
def eliminar_cliente(cliente_id):
    flash(f'Funcionalidad "Eliminar Cliente {cliente_id}" no implementada.', 'warning')
    return redirect(url_for('listar_clientes'))

# --- GESTIÓN DE STAFF ---
@app.route('/staff')
def listar_staff():
    staff = cargar_datos(STAFF_FILE)
    return render_template('staff.html', staff=staff, filters={})

@app.route('/staff/nuevo', methods=['GET', 'POST'])
def nuevo_staff():
    flash('Funcionalidad "Añadir Staff" no implementada.', 'warning')
    return redirect(url_for('listar_staff'))

@app.route('/staff/eliminar/<staff_id>')
def eliminar_staff(staff_id):
    flash(f'Funcionalidad "Eliminar Staff {staff_id}" no implementada.', 'warning')
    return redirect(url_for('listar_staff'))

# --- GESTIÓN DE RECORDATORIOS ---
@app.route('/recordatorios')
def listar_recordatorios():
    recordatorios = cargar_datos(RECORDATORIOS_FILE)
    staff = {s['id']: s['nombre'] for s in cargar_datos(STAFF_FILE)}
    return render_template('recordatorios.html', recordatorios=recordatorios, staff=staff, all_staff=cargar_datos(STAFF_FILE), filters={})

@app.route('/recordatorios/nuevo', methods=['POST'])
def nuevo_recordatorio():
    try:
        data = request.get_json()
        if not data or 'titulo' not in data or 'fecha' not in data:
            return jsonify({'status': 'error', 'message': 'Datos incompletos.'}), 400

        recordatorios = cargar_datos(RECORDATORIOS_FILE)
        
        nuevo = {
            'id': generar_id(),
            'titulo': data['titulo'],
            'fecha': data['fecha'],
            'staff_id': data.get('staff_id'),
            'completado': False,
            'creado_en': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        recordatorios.append(nuevo)
        guardar_datos(RECORDATORIOS_FILE, recordatorios)
        
        return jsonify({'status': 'success', 'message': 'Recordatorio creado con éxito.', 'recordatorio': nuevo}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/recordatorios/eliminar/<recordatorio_id>', methods=['POST'])
def eliminar_recordatorio(recordatorio_id):
    try:
        recordatorios = cargar_datos(RECORDATORIOS_FILE)
        recordatorios_filtrados = [r for r in recordatorios if r.get('id') != recordatorio_id]
        
        if len(recordatorios_filtrados) < len(recordatorios):
            guardar_datos(RECORDATORIOS_FILE, recordatorios_filtrados)
            return jsonify({'status': 'success', 'message': 'Recordatorio eliminado.'})
        else:
            return jsonify({'status': 'error', 'message': 'Recordatorio no encontrado.'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
