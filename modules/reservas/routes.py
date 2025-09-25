from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from modules.reservas.services import (
    obtener_reservas_filtradas, 
    crear_reserva, 
    obtener_lanzamientos_todos, 
    obtener_clientes_todos,
    obtener_reserva_por_id,
    actualizar_reserva,
    obtener_eventos_todos,
    eliminar_reserva as eliminar_reserva_servicio
)
from modules.lanzamientos.services import obtener_juegos_y_colecciones

reservas_bp = Blueprint('reservas', __name__, url_prefix='/reservas')

@reservas_bp.route('/')
def listar_reservas():
    filters = {
        'q': request.args.get('q', ''),
        'start_date': request.args.get('start_date', ''),
        'end_date': request.args.get('end_date', ''),
        'payment_status': request.args.get('payment_status', '')
    }
    reservas, total_pendiente = obtener_reservas_filtradas(filters)
    return render_template('reservas/reservas.html', reservas=reservas, total_pendiente=total_pendiente, filters=filters)

@reservas_bp.route('/nueva', methods=['GET', 'POST'])
def nueva_reserva():
    if request.method == 'POST':
        datos_reserva = request.form.to_dict()
        crear_reserva(datos_reserva)
        flash('Reserva creada con éxito.', 'success')
        return redirect(url_for('reservas.listar_reservas'))

    lanzamientos = obtener_lanzamientos_todos()
    clientes = obtener_clientes_todos()
    eventos = obtener_eventos_todos()
    juegos_colecciones = obtener_juegos_y_colecciones()
    juegos = list(juegos_colecciones.get('juegos', {}).keys())
    return render_template(
        'reservas/nueva_reserva.html', 
        lanzamientos=lanzamientos, 
        clientes=clientes, 
        eventos=eventos, 
        juegos_colecciones=juegos_colecciones,
        juegos=juegos,
        now=datetime.now()
    )

@reservas_bp.route('/editar/<reserva_id>', methods=['GET', 'POST'])
def editar_reserva(reserva_id):
    reserva = obtener_reserva_por_id(reserva_id)
    if not reserva:
        flash('Reserva no encontrada.', 'danger')
        return redirect(url_for('reservas.listar_reservas'))

    if request.method == 'POST':
        datos_reserva = request.form.to_dict()
        actualizar_reserva(reserva_id, datos_reserva)
        flash('Reserva actualizada con éxito.', 'success')
        return redirect(url_for('reservas.listar_reservas'))

    lanzamientos = obtener_lanzamientos_todos()
    clientes = obtener_clientes_todos()
    eventos = obtener_eventos_todos()
    juegos_colecciones = obtener_juegos_y_colecciones()
    juegos = list(juegos_colecciones.get('juegos', {}).keys())
    
    producto = None
    if reserva.get('lanzamiento_id'):
        producto = next((l for l in lanzamientos if l['id'] == reserva['lanzamiento_id']), None)
    elif reserva.get('evento_id'):
        producto = next((e for e in eventos if e['id'] == reserva['evento_id']), None)

    return render_template(
        'reservas/editar_reserva.html', 
        reserva=reserva, 
        lanzamientos=lanzamientos, 
        clientes=clientes, 
        eventos=eventos,
        juegos_colecciones=juegos_colecciones,
        juegos=juegos,
        producto=producto
    )

@reservas_bp.route('/eliminar/<reserva_id>')
def eliminar_reserva(reserva_id):
    try:
        eliminar_reserva_servicio(reserva_id)
        flash('Reserva eliminada correctamente.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('reservas.listar_reservas'))
