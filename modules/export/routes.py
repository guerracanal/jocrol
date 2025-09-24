
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
    
    data_sources = {
        'clientes.json': 'Clientes',
        'colecciones.json': 'Colecciones',
        'eventos.json': 'Eventos',
        'lanzamientos.json': 'Lanzamientos',
        'reservas.json': 'Reservas'
    }

    if 'Sheet' in wb.sheetnames:
        wb.remove(wb['Sheet'])

    for filename, sheet_name in data_sources.items():
        data = load_data(filename)
        ws = wb.create_sheet(title=sheet_name)

        if not data:
            ws.cell(row=1, column=1, value="No hay datos disponibles.")
            continue

        headers = list(data[0].keys())
        ws.append(headers)

        for item in data:
            row = []
            for header in headers:
                cell_value = item.get(header, '')
                if isinstance(cell_value, (dict, list)):
                    cell_value = str(cell_value)
                row.append(cell_value)
            ws.append(row)

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
    if 'excel_file' not in request.files:
        flash('No se ha seleccionado ningún fichero.', 'danger')
        return redirect(url_for('main.index'))

    file = request.files['excel_file']
    if file.filename == '':
        flash('No se ha seleccionado ningún fichero.', 'danger')
        return redirect(url_for('main.index'))

    if file and file.filename.endswith('.xlsx'):
        filename = secure_filename(file.filename)
        
        try:
            wb = load_workbook(file)
            
            data_sources = {
                'Clientes': 'clientes.json',
                'Colecciones': 'colecciones.json',
                'Eventos': 'eventos.json',
                'Lanzamientos': 'lanzamientos.json',
                'Reservas': 'reservas.json'
            }

            for sheet_name, json_filename in data_sources.items():
                if sheet_name in wb.sheetnames:
                    ws = wb[sheet_name]
                    
                    # Leer cabeceras
                    headers = [cell.value for cell in ws[1]]
                    
                    # Leer filas de datos
                    data = []
                    for row in ws.iter_rows(min_row=2):
                        item = {}
                        for header, cell in zip(headers, row):
                            item[header] = cell.value
                        data.append(item)
                    
                    save_data(json_filename, data)

            flash('Datos importados y actualizados correctamente.', 'success')

        except Exception as e:
            flash(f'Error al procesar el fichero Excel: {e}', 'danger')

    else:
        flash('Formato de fichero no válido. Por favor, sube un fichero .xlsx.', 'danger')

    return redirect(url_for('main.index'))
