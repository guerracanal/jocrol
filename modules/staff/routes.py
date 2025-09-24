from flask import Blueprint, render_template, request, redirect, url_for, flash
from modules.staff.services import obtener_staff_todos

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/')
def listar_staff():
    staff = obtener_staff_todos()
    return render_template('staff/staff.html', staff=staff, filters={})

@staff_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_staff():
    flash('Funcionalidad "Añadir Staff" no implementada.', 'warning')
    return redirect(url_for('staff.listar_staff'))

@staff_bp.route('/editar/<staff_id>', methods=['GET', 'POST'])
def editar_staff(staff_id):
    flash(f'Funcionalidad "Editar Staff {staff_id}" no implementada.', 'warning')
    return redirect(url_for('staff.listar_staff'))

@staff_bp.route('/eliminar/<staff_id>')
def eliminar_staff(staff_id):

    flash(f'Funcionalidad "Eliminar Staff {staff_id}" no implementada.', 'warning')
    return redirect(url_for('staff.listar_staff'))
