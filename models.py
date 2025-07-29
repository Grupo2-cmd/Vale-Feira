from app import db
from flask_login import UserMixin
from datetime import datetime
import hashlib

class Usuario(UserMixin, db.Model):
    """Model for user authentication and management"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False, index=True)
    senha = db.Column(db.String(256), nullable=False)  # SHA-256 hash
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship with products
    produtos = db.relationship('Produto', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, nome, senha, email=None):
        self.nome = nome
        self.senha = self.hash_password(senha)
        self.email = email
    
    @staticmethod
    def hash_password(password):
        """Generate SHA-256 hash for password"""
        if isinstance(password, str):
            password = password.encode('utf-8')
        return hashlib.sha256(password).hexdigest()
    
    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return self.senha == self.hash_password(password)
    
    def get_id(self):
        """Required by Flask-Login"""
        return str(self.id)
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Produto(db.Model):
    """Model for products in the marketplace"""
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, index=True)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    imagem = db.Column(db.String(255), nullable=True)  # Path to image file
    categoria = db.Column(db.String(50), nullable=True, index=True)
    cidade = db.Column(db.String(100), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Foreign key to Usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    def __init__(self, nome, preco, descricao=None, imagem=None, categoria=None, cidade=None, usuario_id=None):
        self.nome = nome
        self.preco = preco
        self.descricao = descricao
        self.imagem = imagem
        self.categoria = categoria
        self.cidade = cidade
        self.usuario_id = usuario_id
    
    @property
    def preco_formatado(self):
        """Return formatted price in Brazilian Real"""
        return f"R$ {self.preco:.2f}".replace('.', ',')
    
    def to_dict(self):
        """Convert product to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'nome': self.nome,
            'preco': self.preco,
            'preco_formatado': self.preco_formatado,
            'descricao': self.descricao,
            'imagem': self.imagem,
            'categoria': self.categoria,
            'cidade': self.cidade,
            'created_at': self.created_at.isoformat(),
            'usuario': self.usuario.nome if self.usuario else None
        }
    
    def __repr__(self):
        return f'<Produto {self.nome}>'
