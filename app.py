import logging
import sys
from flask import Flask

# Configure logging to output to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def create_app():
    logging.info("Iniciando create_app...")
    app = Flask(__name__)
    
    logging.info("Cargando configuración desde objeto...")
    app.config.from_object('config')
    logging.info("Configuración cargada.")

    # Importar filtros
    logging.info("Importando filtros...")
    from common.utils import format_date_filter, format_datetime_filter
    logging.info("Filtros importados.")

    # Registrar filtros
    logging.info("Registrando filtros...")
    app.jinja_env.filters['formato_fecha'] = format_date_filter
    app.jinja_env.filters['formato_fecha_hora'] = format_datetime_filter
    logging.info("Filtros registrados.")

    # Importar y registrar Blueprints
    logging.info("Importando Blueprint: main")
    from modules.main.routes import main_bp
    app.register_blueprint(main_bp)
    logging.info("Blueprint registrado: main")

    logging.info("Importando Blueprint: eventos")
    from modules.eventos.routes import eventos_bp
    app.register_blueprint(eventos_bp)
    logging.info("Blueprint registrado: eventos")

    logging.info("Importando Blueprint: clientes")
    from modules.clientes.routes import clientes_bp
    app.register_blueprint(clientes_bp)
    logging.info("Blueprint registrado: clientes")

    logging.info("Importando Blueprint: lanzamientos")
    from modules.lanzamientos.routes import lanzamientos_bp
    app.register_blueprint(lanzamientos_bp)
    logging.info("Blueprint registrado: lanzamientos")

    logging.info("Importando Blueprint: reservas")
    from modules.reservas.routes import reservas_bp
    app.register_blueprint(reservas_bp)
    logging.info("Blueprint registrado: reservas")

    logging.info("Importando Blueprint: staff")
    from modules.staff.routes import staff_bp
    app.register_blueprint(staff_bp)
    logging.info("Blueprint registrado: staff")

    logging.info("Importando Blueprint: export")
    from modules.export.routes import export_bp
    app.register_blueprint(export_bp)
    logging.info("Blueprint registrado: export")
    
    logging.info("create_app finalizado con éxito.")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
