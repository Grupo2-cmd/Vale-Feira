from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from models import Usuario
from app import db
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.site'))

    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        nome = request.form.get('nomeForm', '').strip()
        senha = request.form.get('senhaForm', '')
        
        # Validation
        if not nome or not senha:
            flash('Nome e senha são obrigatórios.', 'error')
            return render_template('login.html')
        
        # Find user
        user = db.session.query(Usuario).filter_by(nome=nome).first()
        
        if not user or not user.check_password(senha):
            flash('Nome ou senha incorretos.', 'error')
            return render_template('login.html')
        
        if not user.is_active:
            flash('Conta desativada. Entre em contato com o suporte.', 'error')
            return render_template('login.html')
        
        login_user(user)
        flash(f'Bem-vindo, {user.nome}!', 'success')
        
        # Redirect to next page or home
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.site'))
        
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        flash('Erro interno. Tente novamente.', 'error')
        return render_template('login.html')

@auth_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    """User registration route"""
    if request.method == 'GET':
        return render_template('registrar.html')
    
    try:
        nome = request.form.get('nomeForm', '').strip()
        senha = request.form.get('senhaForm', '')
        confirma_senha = request.form.get('confirmaSenhaForm', '')
        email = request.form.get('emailForm', '').strip()
        
        # Validation
        if not nome or not senha:
            flash('Nome e senha são obrigatórios.', 'error')
            return render_template('registrar.html')
        
        if len(nome) < 3:
            flash('Nome deve ter pelo menos 3 caracteres.', 'error')
            return render_template('registrar.html')
        
        if len(senha) < 6:
            flash('Senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('registrar.html')
        
        if senha != confirma_senha:
            flash('Senhas não conferem.', 'error')
            return render_template('registrar.html')
        
        # Check if user already exists
        if db.session.query(Usuario).filter_by(nome=nome).first():
            flash('Nome de usuário já existe.', 'error')
            return render_template('registrar.html')
        
        if email and db.session.query(Usuario).filter_by(email=email).first():
            flash('Email já cadastrado.', 'error')
            return render_template('registrar.html')
        
        # Create new user
        novo_usuario = Usuario(nome=nome, senha=senha, email=email if email else None)
        db.session.add(novo_usuario)
        db.session.commit()
        
        login_user(novo_usuario)
        flash(f'Conta criada com sucesso! Bem-vindo, {nome}!', 'success')
        return redirect(url_for('main.site'))
        
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        db.session.rollback()
        flash('Erro interno. Tente novamente.', 'error')
        return render_template('registrar.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('main.site'))

@auth_bp.route('/redefinir_senha', methods=['GET', 'POST'])
def redefinir_senha():
    """Password reset route"""
    if request.method == 'GET':
        return render_template('redefinir_senha.html')
    
    try:
        nome = request.form.get('nome', '').strip()
        nova_senha = request.form.get('nova_senha', '')
        confirma_senha = request.form.get('confirma_senha', '')
        
        # Validation
        if not nome or not nova_senha or not confirma_senha:
            flash('Todos os campos são obrigatórios.', 'error')
            return render_template('redefinir_senha.html')
        
        if len(nova_senha) < 6:
            flash('Nova senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('redefinir_senha.html')
        
        if nova_senha != confirma_senha:
            flash('Senhas não conferem.', 'error')
            return render_template('redefinir_senha.html')
        
        # Find user
        usuario = db.session.query(Usuario).filter_by(nome=nome).first()
        if not usuario:
            flash('Usuário não encontrado.', 'error')
            return render_template('redefinir_senha.html')
        
        # Update password
        usuario.senha = Usuario.hash_password(nova_senha)
        db.session.commit()
        
        flash('Senha redefinida com sucesso!', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        logging.error(f"Password reset error: {str(e)}")
        db.session.rollback()
        flash('Erro interno. Tente novamente.', 'error')
        return render_template('redefinir_senha.html')
