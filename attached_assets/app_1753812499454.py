from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from database import db
from models import Usuario, Produto
import hashlib
import os
from werkzeug.utils import secure_filename

# Criação da aplicação Flask
app = Flask(__name__)
app.secret_key = 'Yukimura'  # Chave secreta para sessões e cookies

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['UPLOAD_FOLDER'] = 'static/img'  # Pasta para armazenar imagens

db.init_app(app)  # Inicializa a extensão SQLAlchemy com a app

# Função para gerar hash seguro (SHA-256)
def hash(txt):
    hash_obj = hashlib.sha256(txt.encode('utf-8'))
    return hash_obj.hexdigest()

# Configuração do gerenciador de login
lm = LoginManager(app)
lm.login_view = 'login'  # Redireciona para /login se não autenticado

# Função para carregar o usuário logado
@lm.user_loader
def user_loader(id):
    return db.session.query(Usuario).filter_by(id=id).first()

# Página principal: exibe todos os produtos
@app.route('/')
def site():
    produtos = db.session.query(Produto).all()
    return render_template('site.html', produtos=produtos)

# Rota de login
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

# Rota para registrar um novo usuário
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

# Rota para logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('site'))

# Rota para adicionar um produto
@app.route('/adicionar_produtos', methods=['GET', 'POST'])
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

        return redirect(url_for('site'))

    return render_template('adicionar_produtos.html')

# Página alternativa para exibir produtos (caso necessário)
def pagina_produtos():
    produtos = Produto.query.all()
    return render_template('pagina_produtos.html', produtos=produtos)

# Rota para excluir um produto
@app.route('/excluir_produto/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    produto = db.session.query(Produto).filter_by(id=id).first()
    if produto:
        db.session.delete(produto)
        db.session.commit()
    return redirect(url_for('site'))

# Rota para redefinir a senha de um usuário (sem necessidade de login)
@app.route('/redefinir_senha', methods=['GET', 'POST'])
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
        return redirect(url_for('login'))

    return render_template('redefinir_senha.html')

# Execução principal
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Cria as tabelas se não existirem
    app.run(debug=True)  # Inicia o servidor Flask
