from flask import Blueprint, render_template, request, redirect, url_for, flash
from modules.eventos.services import obtener_eventos_todos, obtener_evento_por_id, actualizar_evento, crear_evento
from data.data_manager import cargar_datos, COLECCIONES_FILE

eventos_bp = Blueprint('eventos', __name__, url_prefix='/eventos')

@eventos_bp.route('/')
def listar_eventos():
    q = request.args.get('q', '').lower()
    eventos_todos = obtener_eventos_todos()
    colecciones = cargar_datos(COLECCIONES_FILE)
    colecciones_map = {c['id']: c for c in colecciones if 'id' in c}

    if q:
        eventos_filtrados = [
            e for e in eventos_todos if (
                q in e.get('nombre', '').lower() or
                q in e.get('coleccion', '').lower()
            )
        ]
    else:
        eventos_filtrados = eventos_todos

    for evento in eventos_filtrados:
        coleccion_id = evento.get('coleccion')
        coleccion_data = colecciones_map.get(coleccion_id)
        
        # Asegurar que siempre haya un color válido
        color = '#6c757d'  # Color gris por defecto
        if coleccion_data and coleccion_data.get('color'):
            color = coleccion_data.get('color')
        evento['coleccion_color'] = color

    filters = {'q': q}
    return render_template('eventos/eventos.html', eventos=eventos_filtrados, filters=filters)


@eventos_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo_evento():
    if request.method == 'POST':
        datos_evento = request.form.to_dict()
        crear_evento(datos_evento)
        flash('Evento creado con éxito.', 'success')
        return redirect(url_for('eventos.listar_eventos'))
    return render_template('eventos/nuevo_evento.html')

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

    return render_template('eventos/editar_evento.html', evento=evento)

@eventos_bp.route('/eliminar/<evento_id>')
def eliminar_evento(evento_id):
    flash(f'Funcionalidad "Eliminar Evento {evento_id}" no implementada.', 'warning')
    return redirect(url_for('eventos.listar_eventos'))

@eventos_bp.route('/calendario')
def calendario_eventos():
    eventos = obtener_eventos_todos()
    return render_template('eventos/calendario.html', eventos=eventos)