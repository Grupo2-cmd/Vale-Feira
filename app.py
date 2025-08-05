import os
from flask import Flask
from flask_login import LoginManager
from werkzeug.middleware.proxy_fix import ProxyFix
from database import db
from models import Usuario, Produto, Chat
from routes import auth_bp, produto_bp, main_bp, chat_bp
from routes.perfil import perfil_bp
from flask_wtf import CSRFProtect

# Criação da aplicação Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "Yukimura")

# ---- Proteção CSRF ----
csrf = CSRFProtect(app)

# (opcional) garantir que csrf_token() esteja disponível em templates
@app.context_processor
def inject_csrf_token():
    from flask_wtf.csrf import generate_csrf
    return dict(csrf_token=generate_csrf)

# Configuração do middleware para proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Inicializa a extensão SQLAlchemy com a app
db.init_app(app)

# Configuração do gerenciador de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Você precisa fazer login para acessar esta página.'
login_manager.login_message_category = 'info'

# Função para carregar o usuário logado
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))   # forma recomendada pelo SQLAlchemy 2.x

# Registrar blueprints
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(produto_bp)
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(perfil_bp)

# Criar tabelas do banco de dados (somente primeira vez)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
