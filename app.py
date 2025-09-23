from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Archivos de datos JSON
DATA_DIR = 'data'
LANZAMIENTOS_FILE = os.path.join(DATA_DIR, 'lanzamientos.json')
CLIENTES_FILE = os.path.join(DATA_DIR, 'clientes.json')
RESERVAS_FILE = os.path.join(DATA_DIR, 'reservas.json')

# Crear directorio de datos si no existe
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def cargar_datos(archivo):
    """Carga datos desde un archivo JSON"""
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_datos(archivo, datos):
    """Guarda datos en un archivo JSON"""
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def generar_id():
    """Genera un ID único"""
    return str(uuid.uuid4())

# Rutas principales
@app.route('/')
def index():
    return render_template('index.html')

# GESTIÓN DE LANZAMIENTOS
@app.route('/lanzamientos')
def listar_lanzamientos():
    lanzamientos = cargar_datos(LANZAMIENTOS_FILE)
    return render_template('lanzamientos.html', lanzamientos=lanzamientos)

@app.route('/lanzamientos/nuevo', methods=['GET', 'POST'])
def nuevo_lanzamiento():
    if request.method == 'POST':
        lanzamientos = cargar_datos(LANZAMIENTOS_FILE)
        
        nuevo = {
            'id': generar_id(),
            'nombre': request.form['nombre'],
            'coleccion': request.form['coleccion'],
            'fecha_salida': request.form['fecha_salida'],
            'precio': float(request.form['precio']),
            'reserva': float(request.form['reserva']),
            'tipo': request.form['tipo']  # Marvel's Spiderman, EVENTOS, Avatar
        }
        
        lanzamientos.append(nuevo)
        guardar_datos(LANZAMIENTOS_FILE, lanzamientos)
        flash('Lanzamiento creado exitosamente')
        return redirect(url_for('listar_lanzamientos'))
    
    return render_template('nuevo_lanzamiento.html')

@app.route('/lanzamientos/<lanzamiento_id>/eliminar')
def eliminar_lanzamiento(lanzamiento_id):
    lanzamientos = cargar_datos(LANZAMIENTOS_FILE)
    lanzamientos = [l for l in lanzamientos if l['id'] != lanzamiento_id]
    guardar_datos(LANZAMIENTOS_FILE, lanzamientos)
    flash('Lanzamiento eliminado exitosamente')
    return redirect(url_for('listar_lanzamientos'))

# GESTIÓN DE CLIENTES
@app.route('/clientes')
def listar_clientes():
    clientes = cargar_datos(CLIENTES_FILE)
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        clientes = cargar_datos(CLIENTES_FILE)
        
        nuevo = {
            'id': generar_id(),
            'nombre': request.form['nombre'],
            'email': request.form['email'],
            'telefono': request.form['telefono'],
            'fecha_registro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        clientes.append(nuevo)
        guardar_datos(CLIENTES_FILE, clientes)
        flash('Cliente creado exitosamente')
        return redirect(url_for('listar_clientes'))
    
    return render_template('nuevo_cliente.html')

# GESTIÓN DE RESERVAS
@app.route('/reservas')
def listar_reservas():
    reservas = cargar_datos(RESERVAS_FILE)
    lanzamientos = cargar_datos(LANZAMIENTOS_FILE)
    clientes = cargar_datos(CLIENTES_FILE)
    
    # Enriquecer reservas con datos de lanzamientos y clientes
    reservas_enriquecidas = []
    for reserva in reservas:
        reserva_copia = reserva.copy()
        
        # Buscar datos del lanzamiento
        lanzamiento = next((l for l in lanzamientos if l['id'] == reserva['lanzamiento_id']), None)
        reserva_copia['lanzamiento'] = lanzamiento
        
        # Buscar datos del cliente
        cliente = next((c for c in clientes if c['id'] == reserva['cliente_id']), None)
        reserva_copia['cliente'] = cliente
        
        reservas_enriquecidas.append(reserva_copia)
    
    return render_template('reservas.html', reservas=reservas_enriquecidas)

@app.route('/reservas/nueva', methods=['GET', 'POST'])
def nueva_reserva():
    if request.method == 'POST':
        reservas = cargar_datos(RESERVAS_FILE)
        
        nueva = {
            'id': generar_id(),
            'lanzamiento_id': request.form['lanzamiento_id'],
            'cliente_id': request.form['cliente_id'],
            'cantidad': int(request.form['cantidad']),
            'fecha_reserva': request.form['fecha_reserva'] or datetime.now().strftime('%Y-%m-%d'),
            'pagado': request.form.get('pagado') == 'on',
            'notas': request.form['notas'],
            'estado': 'pendiente'  # pendiente, confirmada, cancelada
        }
        
        reservas.append(nueva)
        guardar_datos(RESERVAS_FILE, reservas)
        flash('Reserva creada exitosamente')
        return redirect(url_for('listar_reservas'))
    
    lanzamientos = cargar_datos(LANZAMIENTOS_FILE)
    clientes = cargar_datos(CLIENTES_FILE)
    return render_template('nueva_reserva.html', lanzamientos=lanzamientos, clientes=clientes)

@app.route('/reservas/<reserva_id>/estado', methods=['POST'])
def cambiar_estado_reserva(reserva_id):
    reservas = cargar_datos(RESERVAS_FILE)
    nuevo_estado = request.form['estado']
    
    for reserva in reservas:
        if reserva['id'] == reserva_id:
            reserva['estado'] = nuevo_estado
            break
    
    guardar_datos(RESERVAS_FILE, reservas)
    flash(f'Estado de reserva actualizado a {nuevo_estado}')
    return redirect(url_for('listar_reservas'))

@app.route('/reservas/<reserva_id>/editar', methods=['GET', 'POST'])
def editar_reserva(reserva_id):
    reservas = cargar_datos(RESERVAS_FILE)
    reserva = next((r for r in reservas if r['id'] == reserva_id), None)
    
    if not reserva:
        flash('Reserva no encontrada')
        return redirect(url_for('listar_reservas'))
    
    if request.method == 'POST':
        reserva.update({
            'cantidad': int(request.form['cantidad']),
            'fecha_reserva': request.form['fecha_reserva'],
            'pagado': request.form.get('pagado') == 'on',
            'notas': request.form['notas']
        })
        
        guardar_datos(RESERVAS_FILE, reservas)
        flash('Reserva actualizada exitosamente')
        return redirect(url_for('listar_reservas'))
    
    lanzamientos = cargar_datos(LANZAMIENTOS_FILE)
    clientes = cargar_datos(CLIENTES_FILE)
    return render_template('editar_reserva.html', reserva=reserva, lanzamientos=lanzamientos, clientes=clientes)

# API para obtener reservas de un lanzamiento
@app.route('/api/lanzamientos/<lanzamiento_id>/reservas')
def api_reservas_lanzamiento(lanzamiento_id):
    reservas = cargar_datos(RESERVAS_FILE)
    clientes = cargar_datos(CLIENTES_FILE)
    
    reservas_lanzamiento = [r for r in reservas if r['lanzamiento_id'] == lanzamiento_id]
    
    # Enriquecer con datos de clientes
    for reserva in reservas_lanzamiento:
        cliente = next((c for c in clientes if c['id'] == reserva['cliente_id']), None)
        reserva['cliente'] = cliente
    
    return jsonify(reservas_lanzamiento)

# API para obtener reservas de un cliente  
@app.route('/api/clientes/<cliente_id>/reservas')
def api_reservas_cliente(cliente_id):
    reservas = cargar_datos(RESERVAS_FILE)
    lanzamientos = cargar_datos(LANZAMIENTOS_FILE)
    
    reservas_cliente = [r for r in reservas if r['cliente_id'] == cliente_id]
    
    # Enriquecer con datos de lanzamientos
    for reserva in reservas_cliente:
        lanzamiento = next((l for l in lanzamientos if l['id'] == reserva['lanzamiento_id']), None)
        reserva['lanzamiento'] = lanzamiento
    
    return jsonify(reservas_cliente)

# VISTA DE CALENDARIO
@app.route('/calendario')
def calendario():
    lanzamientos = cargar_datos(LANZAMIENTOS_FILE)
    return render_template('calendario.html', lanzamientos=lanzamientos)

@app.route('/api/eventos')
def api_eventos():
    """API para obtener eventos del calendario"""
    lanzamientos = cargar_datos(LANZAMIENTOS_FILE)
    eventos = []
    
    for lanzamiento in lanzamientos:
        color = '#007bff'  # Azul por defecto
        if lanzamiento['tipo'] == 'EVENTOS':
            color = '#dc3545'  # Rojo para eventos
        elif lanzamiento['tipo'] == 'Avatar':
            color = '#ffc107'  # Amarillo para Avatar
        
        evento = {
            'id': lanzamiento['id'],
            'title': f"{lanzamiento['nombre']} ({lanzamiento['coleccion']})",
            'start': lanzamiento['fecha_salida'],
            'color': color,
            'extendedProps': {
                'precio': lanzamiento['precio'],
                'reserva': lanzamiento['reserva']
            }
        }
        eventos.append(evento)
    
    return jsonify(eventos)

if __name__ == '__main__':
    app.run(debug=True)