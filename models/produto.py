from database import db
<<<<<<< HEAD
from datetime import datetime

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    preco = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(50), nullable=True)
    cidade = db.Column(db.String(80), nullable=True)
    imagem = db.Column(db.String(200), nullable=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira para usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    def __repr__(self):
        return f'<Produto {self.nome}>'
=======

class Produto(db.Model):
    __tablename__ = 'produtos'  # (opcional, mas recomendado)

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(300))
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(100))
>>>>>>> 6d72f570dcc41bfdfae37938747ff76c9e16f441
