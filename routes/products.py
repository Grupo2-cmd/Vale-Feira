from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from models import Produto
from app import db
from werkzeug.utils import secure_filename
import os
import logging

products_bp = Blueprint('products', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@products_bp.route('/adicionar_produtos', methods=['GET', 'POST'])
@login_required
def adicionar_produtos():
    """Add new product route"""
    if request.method == 'GET':
        return render_template('adicionar_produtos.html')
    
    try:
        nome = request.form.get('nome', '').strip()
        preco_str = request.form.get('preco', '').strip()
        descricao = request.form.get('descricao', '').strip()
        categoria = request.form.get('categoria', '').strip()
        cidade = request.form.get('cidade', '').strip()
        imagem = request.files.get('imagem')
        
        # Validation
        if not nome:
            flash('Nome do produto é obrigatório.', 'error')
            return render_template('adicionar_produtos.html')
        
        if not preco_str:
            flash('Preço é obrigatório.', 'error')
            return render_template('adicionar_produtos.html')
        
        try:
            preco = float(preco_str.replace(',', '.'))
            if preco <= 0:
                raise ValueError("Preço deve ser positivo")
        except ValueError:
            flash('Preço inválido. Use apenas números.', 'error')
            return render_template('adicionar_produtos.html')
        
        # Handle image upload
        caminho_relativo = None
        if imagem and imagem.filename != '':
            if not allowed_file(imagem.filename):
                flash('Tipo de arquivo não permitido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'error')
                return render_template('adicionar_produtos.html')
            
            filename = secure_filename(imagem.filename)
            # Add timestamp to avoid filename conflicts
            import time
            timestamp = str(int(time.time()))
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            caminho_relativo = os.path.join('uploads', filename)
            caminho_completo = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            try:
                imagem.save(caminho_completo)
                logging.info(f"Image saved: {caminho_completo}")
            except Exception as e:
                logging.error(f"Error saving image: {str(e)}")
                flash('Erro ao salvar imagem.', 'error')
                return render_template('adicionar_produtos.html')
        
        # Create new product
        novo_produto = Produto(
            nome=nome,
            preco=preco,
            descricao=descricao if descricao else None,
            imagem=caminho_relativo,
            categoria=categoria if categoria else None,
            cidade=cidade if cidade else None,
            usuario_id=current_user.id
        )
        
        db.session.add(novo_produto)
        db.session.commit()
        
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('main.site'))
        
    except Exception as e:
        logging.error(f"Error adding product: {str(e)}")
        db.session.rollback()
        flash('Erro interno. Tente novamente.', 'error')
        return render_template('adicionar_produtos.html')

@products_bp.route('/meus_produtos')
@login_required
def meus_produtos():
    """Display user's products"""
    try:
        produtos = db.session.query(Produto).filter_by(
            usuario_id=current_user.id,
            is_active=True
        ).order_by(Produto.created_at.desc()).all()
        
        return render_template('meus_produtos.html', produtos=produtos)
        
    except Exception as e:
        logging.error(f"Error loading user products: {str(e)}")
        flash('Erro ao carregar produtos.', 'error')
        return render_template('meus_produtos.html', produtos=[])

@products_bp.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_produto(id):
    """Edit product route"""
    produto = db.session.get(Produto, id)
    
    if not produto or produto.usuario_id != current_user.id:
        flash('Produto não encontrado ou acesso negado.', 'error')
        return redirect(url_for('products.meus_produtos'))
    
    if request.method == 'GET':
        return render_template('editar_produto.html', produto=produto)
    
    try:
        nome = request.form.get('nome', '').strip()
        preco_str = request.form.get('preco', '').strip()
        descricao = request.form.get('descricao', '').strip()
        categoria = request.form.get('categoria', '').strip()
        cidade = request.form.get('cidade', '').strip()
        imagem = request.files.get('imagem')
        
        # Validation
        if not nome:
            flash('Nome do produto é obrigatório.', 'error')
            return render_template('editar_produto.html', produto=produto)
        
        if not preco_str:
            flash('Preço é obrigatório.', 'error')
            return render_template('editar_produto.html', produto=produto)
        
        try:
            preco = float(preco_str.replace(',', '.'))
            if preco <= 0:
                raise ValueError("Preço deve ser positivo")
        except ValueError:
            flash('Preço inválido. Use apenas números.', 'error')
            return render_template('editar_produto.html', produto=produto)
        
        # Update product fields
        produto.nome = nome
        produto.preco = preco
        produto.descricao = descricao if descricao else None
        produto.categoria = categoria if categoria else None
        produto.cidade = cidade if cidade else None
        
        # Handle new image upload
        if imagem and imagem.filename != '':
            if not allowed_file(imagem.filename):
                flash('Tipo de arquivo não permitido. Use PNG, JPG, JPEG, GIF ou WEBP.', 'error')
                return render_template('editar_produto.html', produto=produto)
            
            # Delete old image if exists
            if produto.imagem:
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                      os.path.basename(produto.imagem))
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        logging.warning(f"Could not delete old image: {str(e)}")
            
            filename = secure_filename(imagem.filename)
            import time
            timestamp = str(int(time.time()))
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            caminho_relativo = os.path.join('uploads', filename)
            caminho_completo = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            try:
                imagem.save(caminho_completo)
                produto.imagem = caminho_relativo
                logging.info(f"Image updated: {caminho_completo}")
            except Exception as e:
                logging.error(f"Error saving new image: {str(e)}")
                flash('Erro ao salvar nova imagem.', 'error')
                return render_template('editar_produto.html', produto=produto)
        
        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('products.meus_produtos'))
        
    except Exception as e:
        logging.error(f"Error updating product: {str(e)}")
        db.session.rollback()
        flash('Erro interno. Tente novamente.', 'error')
        return render_template('editar_produto.html', produto=produto)

@products_bp.route('/excluir_produto/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    """Delete product route"""
    try:
        produto = db.session.get(Produto, id)
        
        if not produto or produto.usuario_id != current_user.id:
            flash('Produto não encontrado ou acesso negado.', 'error')
            return redirect(url_for('products.meus_produtos'))
        
        # Delete image file if exists
        if produto.imagem:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                    os.path.basename(produto.imagem))
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    logging.info(f"Image deleted: {image_path}")
                except Exception as e:
                    logging.warning(f"Could not delete image: {str(e)}")
        
        # Soft delete - just mark as inactive
        produto.is_active = False
        db.session.commit()
        
        flash('Produto removido com sucesso!', 'success')
        
    except Exception as e:
        logging.error(f"Error deleting product: {str(e)}")
        db.session.rollback()
        flash('Erro ao remover produto.', 'error')
    
    return redirect(url_for('products.meus_produtos'))
