
import json
import io
import os
from flask import Blueprint, request, redirect, url_for, flash, send_file
from openpyxl import Workbook, load_workbook
from werkzeug.utils import secure_filename

export_bp = Blueprint('export', __name__, url_prefix='/export')

# Obtener la ruta absoluta al directorio 'data'
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))

def load_data(filename):
    """Carga datos desde un fichero JSON en el directorio data."""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(filename, data):
    """Guarda datos en un fichero JSON en el directorio data."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@export_bp.route('/excel')
def export_excel():
    """Exporta todos los datos a un único fichero Excel con múltiples hojas."""
    wb = Workbook()
    if 'Sheet' in wb.sheetnames:
        wb.remove(wb['Sheet']) # Eliminar la hoja por defecto

    # 1. Tratamiento especial para juegos_colecciones.json
    juegos_data = load_data('juegos_colecciones.json')
    ws_juegos = wb.create_sheet(title='Juegos')
    ws_juegos.append(['Juego', 'Color'])
    ws_colecciones = wb.create_sheet(title='Colecciones')
    ws_colecciones.append(['Coleccion', 'Juego'])

    if isinstance(juegos_data, dict) and 'juegos' in juegos_data:
        for juego, details in juegos_data['juegos'].items():
            ws_juegos.append([juego, details.get('color', '')])
            for coleccion in details.get('colecciones', []):
                ws_colecciones.append([coleccion, juego])

    # 2. Tratamiento para el resto de los ficheros
    standard_data_sources = {
        'clientes.json': 'Clientes',
        'eventos.json': 'Eventos',
        'lanzamientos.json': 'Lanzamientos',
        'reservas.json': 'Reservas'
    }

    for filename, sheet_name in standard_data_sources.items():
        data = load_data(filename)
        ws = wb.create_sheet(title=sheet_name)

        if not data or not isinstance(data, list) or not any(data):
            ws.cell(row=1, column=1, value="No hay datos disponibles.")
            continue
        
        headers = list(next((item for item in data if item), {}).keys())
        if not headers:
            ws.cell(row=1, column=1, value="No hay datos disponibles.")
            continue

        ws.append(headers)
        for item in data:
            if not item:
                continue
            row = [item.get(h, '') for h in headers]
            ws.append(row)

    # Guardar el fichero en memoria
    excel_stream = io.BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)

    return send_file(
        excel_stream,
        as_attachment=True,
        download_name='export_gestion_lanzamientos.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@export_bp.route('/import/excel', methods=['POST'])
def import_excel():
    """Importa datos desde un fichero Excel y sobrescribe los ficheros JSON."""
    if 'excel_file' not in request.files or not request.files['excel_file'].filename:
        flash('No se ha seleccionado ningún fichero.', 'danger')
        return redirect(url_for('main.index'))

    file = request.files['excel_file']

    if not file.filename.endswith('.xlsx'):
        flash('Formato de fichero no válido. Por favor, sube un fichero .xlsx.', 'danger')
        return redirect(url_for('main.index'))

    try:
        wb = load_workbook(file)

        # 1. Reconstruir juegos_colecciones.json desde las hojas "Juegos" y "Colecciones"
        reconstructed_juegos = {}
        if 'Juegos' in wb.sheetnames:
            ws_juegos = wb['Juegos']
            if ws_juegos.max_row > 1:
                headers = [cell.value for cell in ws_juegos[1]]
                juego_idx = headers.index('Juego')
                color_idx = headers.index('Color')
                for row in ws_juegos.iter_rows(min_row=2):
                    juego_name = row[juego_idx].value
                    if juego_name:
                        reconstructed_juegos[juego_name] = {
                            'color': row[color_idx].value or '',
                            'colecciones': []
                        }
        
        if 'Colecciones' in wb.sheetnames:
            ws_colecciones = wb['Colecciones']
            if ws_colecciones.max_row > 1:
                headers = [cell.value for cell in ws_colecciones[1]]
                coleccion_idx = headers.index('Coleccion')
                juego_idx = headers.index('Juego')
                for row in ws_colecciones.iter_rows(min_row=2):
                    coleccion_name = row[coleccion_idx].value
                    juego_name = row[juego_idx].value
                    if coleccion_name and juego_name and juego_name in reconstructed_juegos:
                        reconstructed_juegos[juego_name]['colecciones'].append(coleccion_name)

        # Envolver la estructura reconstruida en la clave 'juegos'
        final_juegos_structure = {"juegos": reconstructed_juegos}
        save_data('juegos_colecciones.json', final_juegos_structure)

        # 2. Importar el resto de las hojas
        standard_data_sources = {
            'Clientes': 'clientes.json',
            'Eventos': 'eventos.json',
            'Lanzamientos': 'lanzamientos.json',
            'Reservas': 'reservas.json'
        }

        for sheet_name, json_filename in standard_data_sources.items():
            if sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                if ws.max_row <= 1:
                    save_data(json_filename, [])
                    continue

                headers = [cell.value for cell in ws[1]]
                data = []
                for row in ws.iter_rows(min_row=2):
                    if all(cell.value is None for cell in row):
                        continue
                    item = {header: cell.value for header, cell in zip(headers, row) if header}
                    data.append(item)
                save_data(json_filename, data)

        flash('Datos importados y actualizados correctamente.', 'success')

    except Exception as e:
        flash(f'Error al procesar el fichero Excel: {e}', 'danger')

    return redirect(url_for('main.index'))
