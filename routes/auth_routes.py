from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from models.usuario import Usuario
from database import db
import hashlib
from .forms import LoginForm
from .forms import RegistrarForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        nome = form.nomeForm.data
        senha = form.senhaForm.data

        usuario = Usuario.query.filter_by(nome=nome).first()
        if usuario:
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            if usuario.senha_hash == senha_hash:
                login_user(usuario)
                flash(f'Bem-vindo, {usuario.nome}!', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Senha incorreta.', 'error')
        else:
            flash('Usuário não encontrado.', 'error')
    
    return render_template('login.html', form=form)


@auth_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    form = RegistrarForm()

    if form.validate_on_submit():
        nome = form.nomeForm.data
        senha = form.senhaForm.data
        confirma_senha = form.confirmaSenhaForm.data
        email = form.emailForm.data

        # Verificar se usuário já existe
        if Usuario.query.filter_by(nome=nome).first():
            flash('Nome de usuário já existe.', 'error')
            return render_template('registrar.html', form=form)

        # Criar usuário e salvar no banco
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        novo_usuario = Usuario(nome=nome, senha_hash=senha_hash, email=email or None)

        try:
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Conta criada com sucesso! Você pode fazer login agora.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.', 'error')

    # GET ou formulário inválido cai aqui:
    return render_template('registrar.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu com sucesso.', 'info')
    return redirect(url_for('main.home'))

from .forms import RedefinirSenhaForm

@auth_bp.route('/redefinir_senha', methods=['GET', 'POST'])
def redefinir_senha():
    form = RedefinirSenhaForm()
    if form.validate_on_submit():
        nome = form.nomeForm.data
        nova_senha = form.novaSenhaForm.data
        # A confirmação já é validada pelo EqualTo

        usuario = Usuario.query.filter_by(nome=nome).first()
        if not usuario:
            flash('Usuário não encontrado.', 'error')
            return render_template('redefinir_senha.html', form=form)
        
        usuario.senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
        try:
            db.session.commit()
            flash('Senha redefinida com sucesso! Você pode fazer login agora.', 'success')
            return redirect(url_for('auth.login'))
        except Exception:
            db.session.rollback()
            flash('Erro ao redefinir senha. Tente novamente.', 'error')

    return render_template('redefinir_senha.html', form=form)
