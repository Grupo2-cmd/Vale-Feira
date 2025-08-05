<<<<<<< HEAD
from database import db
from flask_login import UserMixin
from datetime import datetime
import hashlib

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com produtos
    produtos = db.relationship('Produto', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'
=======
from flask_login import UserMixin
from database import db

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(30), unique=True)
    senha = db.Column(db.String())
>>>>>>> 6d72f570dcc41bfdfae37938747ff76c9e16f441
