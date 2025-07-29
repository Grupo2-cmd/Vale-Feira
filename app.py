import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from flask import Flask
from flask_login import LoginManager
from database import db
from models import Usuario
from routes.auth_routes import auth_routes
from routes.produto import produto_routes

app = Flask(__name__)
app.secret_key = 'Yukimura'

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['UPLOAD_FOLDER'] = 'static/img'

db.init_app(app)

lm = LoginManager(app)
lm.login_view = 'auth_routes.login'

@lm.user_loader
def user_loader(id):
    return db.session.query(Usuario).filter_by(id=id).first()

app.register_blueprint(auth_routes)
app.register_blueprint(produto_routes)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
