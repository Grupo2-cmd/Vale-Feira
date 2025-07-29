import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "Yukimura")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Middleware for proxy support
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Enable CORS
    CORS(app)
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models import Usuario
        return db.session.get(Usuario, int(user_id))
    
    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.products import products_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    @app.errorhandler(413)
    def too_large(error):
        return 'Arquivo muito grande! Tamanho máximo permitido: 16MB', 413
    
    # Create database tables
    with app.app_context():
        # Import models to ensure they are registered
        import models
        db.create_all()
        logging.info("Database tables created successfully")
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
