from flask import Blueprint, render_template, request, redirect, url_for, flash
from modules.clientes.services import (
    obtener_clientes_con_reservas, 
    crear_cliente, 
    eliminar_cliente as eliminar_cliente_servicio,
    obtener_cliente_por_id,
    actualizar_cliente
)

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@clientes_bp.route('/')
def listar_clientes():
    q_filter = request.args.get('q', '')
    clientes = obtener_clientes_con_reservas(q_filter)
    return render_template('clientes/clientes.html', clientes=clientes, filters={'q': q_filter})

@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        
        try:
            crear_cliente(nombre=nombre, email=email, telefono=telefono)
            flash('Cliente añadido correctamente.', 'success')
            return redirect(url_for('clientes.listar_clientes'))
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('clientes/nuevo_cliente.html', form_data=request.form)

    return render_template('clientes/nuevo_cliente.html', form_data={})

@clientes_bp.route('/editar/<cliente_id>', methods=['GET', 'POST'])
def editar_cliente(cliente_id):
    cliente = obtener_cliente_por_id(cliente_id)
    if not cliente:
        flash('Cliente no encontrado.', 'danger')
        return redirect(url_for('clientes.listar_clientes'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        
        try:
            actualizar_cliente(cliente_id, nombre, email, telefono)
            flash('Cliente actualizado correctamente.', 'success')
            return redirect(url_for('clientes.listar_clientes'))
        except ValueError as e:
            flash(str(e), 'danger')
            # Recargamos los datos del cliente con los datos del formulario para que el usuario no pierda los cambios
            cliente['nombre'] = nombre
            cliente['email'] = email
            cliente['telefono'] = telefono
            return render_template('clientes/editar_cliente.html', cliente=cliente)

    return render_template('clientes/editar_cliente.html', cliente=cliente)

@clientes_bp.route('/eliminar/<cliente_id>')
def eliminar_cliente(cliente_id):
    try:
        eliminar_cliente_servicio(cliente_id)
        flash('Cliente eliminado correctamente.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('clientes.listar_clientes'))
