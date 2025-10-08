from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
import os

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG') or 'default'
    
    from .config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.landing'
    login_manager.login_message_category = 'info'
    mail.init_app(app)

    # Import and register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .two_fa import two_fa as two_fa_blueprint
    app.register_blueprint(two_fa_blueprint)
    
    from .profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint)
    
    from .tracking import tracking as tracking_blueprint
    app.register_blueprint(tracking_blueprint)

    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    # Add CLI commands
    @app.cli.command('optimize-counters')
    def optimize_counters():
        """Optimize database counters based on actual data"""
        from .models import ShipmentSerialCounter, CombinedShipmentCounter, FileReferenceCounter
        
        # Reset all counters
        serial_count = ShipmentSerialCounter.reset_counter()
        combined_count = CombinedShipmentCounter.reset_counter()
        file_ref_count = FileReferenceCounter.reset_counter()
        
        print(f"Counters optimized:")
        print(f"  - Shipment Serial: {serial_count}")
        print(f"  - Combined Shipment: {combined_count}")
        print(f"  - File Reference: {file_ref_count}")

    return app