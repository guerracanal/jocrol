from flask import Blueprint, render_template, jsonify
from modules.main.services import obtener_eventos_calendario

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/calendario')
def calendario():
    return render_template('calendario.html')

@main_bp.route('/api/eventos')
def api_eventos():
    eventos, error = obtener_eventos_calendario()
    if error:
        return jsonify({"error": error}), 500
    return jsonify(eventos)
