from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from models.usuario import Usuario
from database import db
import hashlib

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form.get('nomeForm')
        senha = request.form.get('senhaForm')
        
        if not nome or not senha:
            flash('Nome de usuário e senha são obrigatórios.', 'error')
            return render_template('login.html')
        
        # Buscar usuário no banco
        usuario = Usuario.query.filter_by(nome=nome).first()
        
        if usuario:
            # Verificar senha usando SHA-256
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            if usuario.senha_hash == senha_hash:
                login_user(usuario)
                flash(f'Bem-vindo, {usuario.nome}!', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Senha incorreta.', 'error')
        else:
            flash('Usuário não encontrado.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        nome = request.form.get('nomeForm')
        senha = request.form.get('senhaForm')
        confirma_senha = request.form.get('confirmaSenhaForm')
        email = request.form.get('emailForm')
        
        # Validações
        if not nome or not senha:
            flash('Nome de usuário e senha são obrigatórios.', 'error')
            return render_template('registrar.html')
        
        if len(nome) < 3:
            flash('Nome de usuário deve ter pelo menos 3 caracteres.', 'error')
            return render_template('registrar.html')
        
        if len(senha) < 6:
            flash('Senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('registrar.html')
        
        if senha != confirma_senha:
            flash('Senhas não conferem.', 'error')
            return render_template('registrar.html')
        
        # Verificar se usuário já existe
        if Usuario.query.filter_by(nome=nome).first():
            flash('Nome de usuário já existe.', 'error')
            return render_template('registrar.html')
        
        # Criar novo usuário
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        novo_usuario = Usuario(
            nome=nome,
            senha_hash=senha_hash,
            email=email if email else None
        )
        
        try:
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Conta criada com sucesso! Você pode fazer login agora.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao criar conta. Tente novamente.', 'error')
    
    return render_template('registrar.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu com sucesso.', 'info')
    return redirect(url_for('main.home'))

@auth_bp.route('/redefinir_senha', methods=['GET', 'POST'])
def redefinir_senha():
    if request.method == 'POST':
        nome = request.form.get('nomeForm')
        nova_senha = request.form.get('novaSenhaForm')
        confirma_senha = request.form.get('confirmaSenhaForm')
        
        if not nome or not nova_senha or not confirma_senha:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('redefinir_senha.html')
        
        if nova_senha != confirma_senha:
            flash('Senhas não conferem.', 'error')
            return render_template('redefinir_senha.html')
        
        if len(nova_senha) < 6:
            flash('Nova senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('redefinir_senha.html')
        
        usuario = Usuario.query.filter_by(nome=nome).first()
        if not usuario:
            flash('Usuário não encontrado.', 'error')
            return render_template('redefinir_senha.html')
        
        # Atualizar senha
        usuario.senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
        
        try:
            db.session.commit()
            flash('Senha redefinida com sucesso! Você pode fazer login agora.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao redefinir senha. Tente novamente.', 'error')
    
    return render_template('redefinir_senha.html')