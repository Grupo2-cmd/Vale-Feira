import hashlib
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from database import db
from models import Usuario

auth_routes = Blueprint('auth_routes', __name__)

def hash(txt):
    return hashlib.sha256(txt.encode('utf-8')).hexdigest()

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('produto_routes.site'))

    if request.method == 'GET':
        return render_template('login.html')
    else:
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']
        user = db.session.query(Usuario).filter_by(nome=nome, senha=hash(senha)).first()

        if not user:
            return 'Nome ou senha incorretos.'

        login_user(user)
        return redirect(url_for('produto_routes.site'))

@auth_routes.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'GET':
        return render_template('registrar.html')

    nome = request.form['nomeForm']
    senha = request.form['senhaForm']

    if db.session.query(Usuario).filter_by(nome=nome).first():
        return render_template('registrar.html', erro='Usuário já cadastrado.')

    novo_usuario = Usuario(nome=nome, senha=hash(senha))
    db.session.add(novo_usuario)
    db.session.commit()
    login_user(novo_usuario)
    return redirect(url_for('produto_routes.site'))

@auth_routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('produto_routes.site'))

@auth_routes.route('/redefinir_senha', methods=['GET', 'POST'])
def redefinir_senha():
    if request.method == 'POST':
        nome = request.form['nome']
        nova_senha = request.form['nova_senha']
        confirma_senha = request.form['confirma_senha']

        if nova_senha != confirma_senha:
            return 'As senhas não conferem.'

        usuario = db.session.query(Usuario).filter_by(nome=nome).first()
        if not usuario:
            return 'Usuário não encontrado.'

        usuario.senha = hash(nova_senha)
        db.session.commit()
        return redirect(url_for('auth_routes.login'))

    return render_template('redefinir_senha.html')
