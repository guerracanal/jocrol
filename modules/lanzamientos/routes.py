from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from modules.lanzamientos.services import (
    obtener_lanzamientos_filtrados, 
    crear_lanzamiento, 
    eliminar_lanzamiento as eliminar_lanzamiento_servicio,
    obtener_lanzamiento_por_id,
    actualizar_lanzamiento,
    obtener_juegos_y_colecciones
)

lanzamientos_bp = Blueprint('lanzamientos', __name__, url_prefix='/lanzamientos')

@lanzamientos_bp.route('/')
def listar_lanzamientos():
    filters = {
        'q': request.args.get('q', ''),
        'juego': request.args.get('juego', ''),
        'start_date': request.args.get('start_date', ''),
        'end_date': request.args.get('end_date', ''),
        'hide_past': request.args.get('hide_past', 'off'),
        'sort_by': request.args.get('sort_by', 'fecha_salida'),
        'sort_order': request.args.get('sort_order', 'asc')
    }
    lanzamientos, _ = obtener_lanzamientos_filtrados(filters)
    juegos_y_colecciones = obtener_juegos_y_colecciones()
    return render_template(
        'lanzamientos/lanzamientos.html', 
        lanzamientos=lanzamientos, 
        juegos=juegos_y_colecciones.get('juegos', {}), 
        filters=filters
    )

@lanzamientos_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_lanzamiento():
    if request.method == 'POST':
        datos_lanzamiento = request.form.to_dict()
        crear_lanzamiento(datos_lanzamiento)
        flash('Lanzamiento añadido con éxito.', 'success')
        return redirect(url_for('lanzamientos.listar_lanzamientos'))
    juegos_y_colecciones = obtener_juegos_y_colecciones()
    return render_template('lanzamientos/nuevo_lanzamiento.html', juegos_y_colecciones=juegos_y_colecciones)

@lanzamientos_bp.route('/editar/<lanzamiento_id>', methods=['GET', 'POST'])
def editar_lanzamiento(lanzamiento_id):
    lanzamiento = obtener_lanzamiento_por_id(lanzamiento_id)
    if not lanzamiento:
        flash('Lanzamiento no encontrado.', 'danger')
        return redirect(url_for('lanzamientos.listar_lanzamientos'))

    if request.method == 'POST':
        datos_lanzamiento = request.form.to_dict()
        actualizar_lanzamiento(lanzamiento_id, datos_lanzamiento)
        flash('Lanzamiento actualizado con éxito.', 'success')
        return redirect(url_for('lanzamientos.listar_lanzamientos'))

    juegos_y_colecciones = obtener_juegos_y_colecciones()
    return render_template('lanzamientos/editar_lanzamiento.html', lanzamiento=lanzamiento, juegos_y_colecciones=juegos_y_colecciones)

@lanzamientos_bp.route('/eliminar/<lanzamiento_id>', methods=['POST'])
def eliminar_lanzamiento(lanzamiento_id):
    eliminar_lanzamiento_servicio(lanzamiento_id)
    flash('Lanzamiento eliminado con éxito.', 'success')
    return redirect(url_for('lanzamientos.listar_lanzamientos'))

@lanzamientos_bp.route('/api/juegos_colecciones')
def api_juegos_colecciones():
    return jsonify(obtener_juegos_y_colecciones())
