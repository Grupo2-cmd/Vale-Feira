import os
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from database import db
from models import Produto
from werkzeug.utils import secure_filename

produto_routes = Blueprint('produto_routes', __name__)

@produto_routes.route('/')
def site():
    produtos = db.session.query(Produto).all()
    return render_template('site.html', produtos=produtos)

@produto_routes.route('/adicionar_produtos', methods=['GET', 'POST'])
@login_required
def adicionar_produtos():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = float(request.form['preco'])
        descricao = request.form['descricao']
        imagem = request.files.get('imagem')

        caminho_relativo = None

        if imagem and imagem.filename != '':
            upload_folder = os.path.join('static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            filename = secure_filename(imagem.filename)
            caminho_relativo = os.path.join('uploads', filename)
            caminho_completo = os.path.join('static', caminho_relativo)
            imagem.save(caminho_completo)

        novo_produto = Produto(
            nome=nome,
            preco=preco,
            descricao=descricao,
            imagem=caminho_relativo if caminho_relativo else ''
        )

        db.session.add(novo_produto)
        db.session.commit()

        return redirect(url_for('produto_routes.site'))

    return render_template('adicionar_produtos.html')

@produto_routes.route('/excluir_produto/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    produto = db.session.query(Produto).filter_by(id=id).first()
    if produto:
        db.session.delete(produto)
        db.session.commit()
    return redirect(url_for('produto_routes.site'))
