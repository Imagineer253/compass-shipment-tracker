from flask import Flask

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Jaiguruji'

    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app