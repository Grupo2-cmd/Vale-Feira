from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.produto import Produto
from database import db
import os

produto_bp = Blueprint('produto', __name__)

@produto_bp.route('/adicionar_produtos', methods=['GET', 'POST'])
@login_required
def adicionar_produtos():
    if request.method == 'POST':
        nome = request.form.get('nomeForm')
        descricao = request.form.get('descricaoForm')
        preco = request.form.get('precoForm')
        categoria = request.form.get('categoriaForm')
        cidade = request.form.get('cidadeForm')
        imagem = request.files.get('imagem')
        
        # Validações
        if not nome or not preco:
            flash('Nome e preço são obrigatórios.', 'error')
            return render_template('adicionar_produtos.html')
        
        try:
            preco_float = float(preco)
            if preco_float <= 0:
                flash('Preço deve ser maior que zero.', 'error')
                return render_template('adicionar_produtos.html')
        except ValueError:
            flash('Preço deve ser um número válido.', 'error')
            return render_template('adicionar_produtos.html')
        
        # Processar upload de imagem
        caminho_relativo = None
        if imagem and imagem.filename and imagem.filename != '':
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filename = secure_filename(imagem.filename)
            if filename:  # secure_filename can return empty string
                caminho_relativo = os.path.join('uploads', filename)
                caminho_completo = os.path.join('static', caminho_relativo)
                imagem.save(caminho_completo)
        
        # Criar novo produto
        novo_produto = Produto(
            nome=nome,
            descricao=descricao,
            preco=preco_float,
            categoria=categoria,
            cidade=cidade,
            imagem=caminho_relativo,
            usuario_id=current_user.id
        )
        
        try:
            db.session.add(novo_produto)
            db.session.commit()
            flash('Produto adicionado com sucesso!', 'success')
            return redirect(url_for('main.home'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao adicionar produto. Tente novamente.', 'error')
    
    return render_template('adicionar_produtos.html')

@produto_bp.route('/excluir_produto/<int:id>')
@login_required
def excluir_produto(id):
    produto = Produto.query.get_or_404(id)
    
    # Verificar se o produto pertence ao usuário atual
    if produto.usuario_id != current_user.id:
        flash('Você não tem permissão para excluir este produto.', 'error')
        return redirect(url_for('main.home'))
    
    try:
        # Remover arquivo de imagem se existir
        if produto.imagem:
            caminho_imagem = os.path.join('static', produto.imagem)
            if os.path.exists(caminho_imagem):
                os.remove(caminho_imagem)
        
        db.session.delete(produto)
        db.session.commit()
        flash('Produto excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir produto. Tente novamente.', 'error')
    
    return redirect(url_for('main.home'))