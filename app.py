from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from database import db
from models import Usuario
import hashlib

app = Flask(__name__)
app.secret_key = 'Yukimura'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

db.init_app(app) 

def hash(txt):
    hash_obj = hashlib.sha256(txt.encode('utf-8'))
    return hash_obj.hexdigest()


lm = LoginManager(app)
lm.login_view = 'login'  


@lm.user_loader
def user_loader(id):
    usuario = db.session.query(Usuario).filter_by(id=id).first()
    return usuario

@app.route('/')
def site():
    return render_template('site.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('site'))
    
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']
        
        user = db.session.query(Usuario).filter_by(nome=nome, senha=hash(senha)).first()
        if not user:
            return 'Nome ou senha incorretos.'
        
        login_user(user)
        return redirect(url_for('site'))

@app.route('/registrar', methods=['GET','POST'])
def registrar():
    if request.method == 'GET':
        return render_template('registrar.html')
    elif request.method == 'POST':
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']
        
        if db.session.query(Usuario).filter_by(nome=nome).first():
            return render_template('registrar.html', erro='Usuário já cadastrado.')
        
        novo_usuario = Usuario(nome=nome, senha=hash(senha))
        db.session.add(novo_usuario)
        db.session.commit()
        
        
        login_user(novo_usuario)
        
        return redirect(url_for('site'))
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('site'))
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
