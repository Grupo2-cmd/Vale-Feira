from database import db

class Produto(db.Model):
    __tablename__ = 'produtos'  # (opcional, mas recomendado)

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(300))
    preco = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(100))
