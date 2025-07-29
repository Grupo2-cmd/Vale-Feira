from flask import Blueprint, render_template, request
from models import Produto
from app import db
import logging

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def site():
    """Main page displaying all active products"""
    try:
        # Get filter parameters
        categoria = request.args.get('categoria', '')
        cidade = request.args.get('cidade', '')
        busca = request.args.get('busca', '')
        
        # Build query
        query = db.session.query(Produto).filter_by(is_active=True)
        
        # Apply filters
        if categoria:
            query = query.filter(Produto.categoria.ilike(f'%{categoria}%'))
        if cidade:
            query = query.filter(Produto.cidade.ilike(f'%{cidade}%'))
        if busca:
            query = query.filter(
                db.or_(
                    Produto.nome.ilike(f'%{busca}%'),
                    Produto.descricao.ilike(f'%{busca}%')
                )
            )
        
        produtos = query.order_by(Produto.created_at.desc()).all()
        
        # Get unique categories and cities for filters
        categorias = db.session.query(Produto.categoria).filter(
            Produto.categoria.isnot(None),
            Produto.is_active == True
        ).distinct().all()
        categorias = [cat[0] for cat in categorias if cat[0]]
        
        cidades = db.session.query(Produto.cidade).filter(
            Produto.cidade.isnot(None),
            Produto.is_active == True
        ).distinct().all()
        cidades = [cidade[0] for cidade in cidades if cidade[0]]
        
        return render_template('site.html', 
                             produtos=produtos,
                             categorias=categorias,
                             cidades=cidades,
                             filtros={
                                 'categoria': categoria,
                                 'cidade': cidade,
                                 'busca': busca
                             })
                             
    except Exception as e:
        logging.error(f"Error loading products: {str(e)}")
        return render_template('site.html', produtos=[], error="Erro ao carregar produtos")

@main_bp.route('/produto/<int:id>')
def produto_detalhes(id):
    """Display detailed view of a single product"""
    try:
        produto = db.session.get(Produto, id)
        if not produto or not produto.is_active:
            return render_template('404.html'), 404
        
        return render_template('produto_detalhes.html', produto=produto)
        
    except Exception as e:
        logging.error(f"Error loading product {id}: {str(e)}")
        return render_template('404.html'), 404
