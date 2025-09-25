
import json
import io
import os
import uuid
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
        if filename == 'juegos_colecciones.json':
            return {"juegos": {}}
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
        wb.remove(wb['Sheet'])

    # Cargar todos los datos necesarios
    juegos_data = load_data('juegos_colecciones.json')
    clientes_data = load_data('clientes.json')
    eventos_data = load_data('eventos.json')
    lanzamientos_data = load_data('lanzamientos.json')
    reservas_data = load_data('reservas.json')

    # Mapeos para búsquedas rápidas
    clientes_map = {c['id']: c for c in clientes_data}
    lanzamientos_map = {l['id']: l for l in lanzamientos_data}
    eventos_map = {e['id']: e for e in eventos_data}

    # 1. Tratamiento para juegos_colecciones.json
    ws_juegos = wb.create_sheet(title='Juegos')
    ws_juegos.append(['Juego', 'Color'])
    ws_colecciones = wb.create_sheet(title='Colecciones')
    ws_colecciones.append(['Coleccion', 'Juego'])

    if isinstance(juegos_data, dict) and 'juegos' in juegos_data:
        for juego, details in juegos_data.get('juegos', {}).items():
            ws_juegos.append([juego, details.get('color', '')])
            for coleccion in details.get('colecciones', []):
                ws_colecciones.append([coleccion, juego])

    # 2. Tratamiento para Clientes, Eventos, Lanzamientos (sin IDs)
    data_sources = {
        'Clientes': clientes_data,
        'Eventos': eventos_data,
        'Lanzamientos': lanzamientos_data
    }

    for sheet_name, data in data_sources.items():
        ws = wb.create_sheet(title=sheet_name)
        if not data:
            ws.cell(row=1, column=1, value="No hay datos disponibles.")
            continue
        
        headers = [key for key in data[0].keys() if key != 'id']
        ws.append(headers)
        for item in data:
            row = [item.get(h, '') for h in headers]
            ws.append(row)

    # 3. Tratamiento especial para Reservas
    ws_reservas = wb.create_sheet(title='Reservas')
    reservas_headers = ['telefono_cliente', 'tipo', 'nombre', 'juego', 'coleccion', 'cantidad', 'fecha_reserva', 'estado', 'pagado', 'tipo_pago', 'notas']
    ws_reservas.append(reservas_headers)

    for reserva in reservas_data:
        cliente_telefono = clientes_map.get(reserva.get('cliente_id'), {}).get('telefono', '-')

        tipo, nombre, juego, coleccion = '', '', '', ''
        item_id = reserva.get('lanzamiento_id') or reserva.get('evento_id')
        item_map = lanzamientos_map if reserva.get('lanzamiento_id') else eventos_map
        
        item = item_map.get(item_id)
        if item:
            tipo = item.get('tipo', '')
            nombre = item.get('nombre', '')
            juego = item.get('juego', '')
            coleccion = item.get('coleccion', '')
        
        row = [
            cliente_telefono,
            tipo,
            nombre,
            juego,
            coleccion,
            reserva.get('cantidad', ''),
            reserva.get('fecha_reserva', ''),
            reserva.get('estado', ''),
            reserva.get('pagado', ''),
            reserva.get('tipo_pago', ''),
            reserva.get('notas', '')
        ]
        ws_reservas.append(row)

    excel_stream = io.BytesIO()
    wb.save(excel_stream)
    excel_stream.seek(0)
    return send_file(excel_stream, as_attachment=True, download_name='export_gestion_lanzamientos.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

"""
@export_bp.route('/import/excel', methods=['POST'])
def import_excel():
    # Importa una hoja específica de un fichero Excel, permitiendo sobrescribir o añadir.
    if 'excel_file' not in request.files or not request.files['excel_file'].filename:
        flash('No se ha seleccionado ningún fichero.', 'danger')
        return redirect(url_for('main.index'))

    file = request.files['excel_file']
    sheet_to_import = request.form.get('sheet_name')
    import_mode = request.form.get('import_mode', 'overwrite')

    if not file.filename.endswith('.xlsx'):
        flash('Formato de fichero no válido. Por favor, sube un fichero .xlsx.', 'danger')
        return redirect(url_for('main.index'))
    if not sheet_to_import:
        flash('No se ha especificado qué hoja importar.', 'danger')
        return redirect(url_for('main.index'))

    try:
        wb = load_workbook(file)
        if sheet_to_import not in wb.sheetnames:
            flash(f"La hoja '{sheet_to_import}' no existe en el fichero.", 'danger')
            return redirect(url_for('main.index'))

        ws = wb[sheet_to_import]
        headers = [cell.value for cell in ws[1]]
        new_data_rows = [dict(zip(headers, [cell.value for cell in row])) for row in ws.iter_rows(min_row=2)]

        # Lógica para 'Juegos' y 'Colecciones'
        if sheet_to_import in ['Juegos', 'Colecciones']:
            data = load_data('juegos_colecciones.json')
            if import_mode == 'overwrite':
                flash('La opción "Sobrescribir" para Juegos/Colecciones reconstruye desde cero.', 'warning')
                if sheet_to_import == 'Juegos':
                    data['juegos'] = {item.get('Juego'): {'color': item.get('Color', ''), 'colecciones': []} for item in new_data_rows}
            else: # Append/Update
                 if sheet_to_import == 'Juegos':
                    for item in new_data_rows:
                        juego = item.get('Juego')
                        if not juego: continue
                        if juego not in data['juegos']:
                            data['juegos'][juego] = {'color': item.get('Color', ''), 'colecciones': []}
                        else:
                            data['juegos'][juego]['color'] = item.get('Color', data['juegos'][juego].get('color', ''))
                 elif sheet_to_import == 'Colecciones':
                    for item in new_data_rows:
                        juego = item.get('Juego')
                        coleccion = item.get('Coleccion')
                        if not juego or not coleccion: continue
                        if juego in data['juegos'] and coleccion not in data['juegos'][juego]['colecciones']:
                            data['juegos'][juego]['colecciones'].append(coleccion)
            save_data('juegos_colecciones.json', data)

        # Lógica para hojas estándar
        else:
            source_map = {'Clientes': 'clientes.json', 'Eventos': 'eventos.json', 'Lanzamientos': 'lanzamientos.json', 'Reservas': 'reservas.json'}
            json_filename = source_map.get(sheet_to_import)
            
            if json_filename:
                if sheet_to_import == 'Reservas':
                    clientes_data = load_data('clientes.json')
                    lanzamientos_data = load_data('lanzamientos.json')
                    eventos_data = load_data('eventos.json')
                    
                    clientes_tel_map = {c['telefono']: c['id'] for c in clientes_data}
                    
                    # Create maps for finding items by their properties
                    lanzamientos_prop_map = {(l.get('tipo'), l.get('nombre'), l.get('juego'), l.get('coleccion')): l['id'] for l in lanzamientos_data}
                    eventos_prop_map = {(e.get('tipo'), e.get('nombre'), e.get('juego'), e.get('coleccion')): e['id'] for e in eventos_data}

                    processed_reservas = []
                    existing_data = load_data(json_filename) if import_mode == 'append' else []
                    max_id = max([int(r['id']) for r in existing_data]) if existing_data else 0

                    for item in new_data_rows:
                        cliente_id = clientes_tel_map.get(item.get('telefono_cliente'))
                        if not cliente_id:
                            flash(f"Cliente con teléfono {item.get('telefono_cliente')} no encontrado. Saltando reserva.", 'warning')
                            continue

                        product_key = (item.get('tipo'), item.get('nombre'), item.get('juego'), item.get('coleccion'))
                        lanzamiento_id = lanzamientos_prop_map.get(product_key)
                        evento_id = eventos_prop_map.get(product_key)

                        if not lanzamiento_id and not evento_id:
                            flash(f"Producto no encontrado para la reserva: {product_key}. Saltando.", 'warning')
                            continue
                        
                        max_id += 1
                        new_reserva = {
                            "id": str(max_id),
                            "cliente_id": cliente_id,
                            "lanzamiento_id": lanzamiento_id,
                            "evento_id": evento_id,
                            "cantidad": item.get('cantidad'),
                            "fecha_reserva": item.get('fecha_reserva', ''),
                            "estado": item.get('estado'),
                            "pagado": item.get('pagado'),
                            "tipo_pago": item.get('tipo_pago'),
                            "notas": item.get('notas', '')
                        }
                        processed_reservas.append(new_reserva)
                    
                    if import_mode == 'overwrite':
                        save_data(json_filename, processed_reservas)
                    else: # append
                        combined_data = existing_data + processed_reservas
                        save_data(json_filename, combined_data)

                elif import_mode == 'overwrite':
                    save_data(json_filename, new_data_rows)
                else: # Append for Clientes, Eventos, Lanzamientos
                    existing_data = load_data(json_filename)
                    # This simple append might create duplicates. For a real-world scenario, you'd want to check for existing records.
                    combined_data = existing_data + new_data_rows
                    save_data(json_filename, combined_data)

        flash(f'Datos de la hoja "{sheet_to_import}" importados correctamente en modo "{import_mode}".', 'success')

    except Exception as e:
        flash(f'Error al procesar el fichero Excel: {e}', 'danger')

    return redirect(url_for('main.index'))
"""
