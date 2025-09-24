from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from modules.eventos.services import (
    obtener_eventos_filtrados,
    obtener_evento_por_id, 
    actualizar_evento, 
    crear_evento,
    eliminar_evento as eliminar_evento_servicio,
    obtener_juegos_y_colecciones
)

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos')

@eventos_bp.route('/')
def listar_eventos():
    filters = {
        'q': request.args.get('q', '')
    }
    eventos = obtener_eventos_filtrados(filters)
    return render_template('eventos/eventos.html', eventos=eventos, filters=filters)


@eventos_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_evento():
    if request.method == 'POST':
        datos_evento = request.form.to_dict()
        crear_evento(datos_evento)
        flash('Evento creado con éxito.', 'success')
        return redirect(url_for('eventos.listar_eventos'))
    juegos_y_colecciones = obtener_juegos_y_colecciones()
    return render_template('eventos/nuevo_evento.html', juegos_y_colecciones=juegos_y_colecciones)

@eventos_bp.route('/editar/<evento_id>', methods=['GET', 'POST'])
def editar_evento(evento_id):
    evento = obtener_evento_por_id(evento_id)
    if not evento:
        flash('Evento no encontrado.', 'danger')
        return redirect(url_for('eventos.listar_eventos'))

    if request.method == 'POST':
        datos_evento = request.form.to_dict()
        actualizar_evento(evento_id, datos_evento)
        flash('Evento actualizado con éxito.', 'success')
        return redirect(url_for('eventos.listar_eventos'))

    juegos_y_colecciones = obtener_juegos_y_colecciones()
    return render_template('eventos/editar_evento.html', evento=evento, juegos_y_colecciones=juegos_y_colecciones)

@eventos_bp.route('/eliminar/<evento_id>', methods=['POST'])
def eliminar_evento(evento_id):
    eliminar_evento_servicio(evento_id)
    flash('Evento eliminado con éxito.', 'success')
    return redirect(url_for('eventos.listar_eventos'))

@eventos_bp.route('/calendario')
def calendario_eventos():
    eventos = obtener_eventos_filtrados({})
    return render_template('eventos/calendario.html', eventos=eventos)

@eventos_bp.route('/api/juegos_colecciones')
def api_juegos_colecciones():
    return jsonify(obtener_juegos_y_colecciones())
