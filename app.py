from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    # Importar filtros
    from common.utils import format_date_filter, format_datetime_filter

    # Registrar filtros
    app.jinja_env.filters['formato_fecha'] = format_date_filter
    app.jinja_env.filters['formato_fecha_hora'] = format_datetime_filter

    # Importar y registrar Blueprints
    from modules.main.routes import main_bp
    from modules.eventos.routes import eventos_bp
    from modules.clientes.routes import clientes_bp
    from modules.lanzamientos.routes import lanzamientos_bp
    from modules.reservas.routes import reservas_bp
    from modules.staff.routes import staff_bp
    from modules.export.routes import export_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(eventos_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(lanzamientos_bp)
    app.register_blueprint(reservas_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(export_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
