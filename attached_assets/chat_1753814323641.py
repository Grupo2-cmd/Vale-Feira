"""
Modelo de chat com criptografia automática
"""
from datetime import datetime
from app import db
from app.utils.crypto import encrypt_chat_message, decrypt_chat_message

class Chat(db.Model):
    """Modelo de Chat com criptografia automática"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    _encrypted_message = db.Column('message', db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    # Relacionamentos
    product = db.relationship('Product', backref='chats')
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_chats')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_chats')

    @property
    def message(self):
        """Descriptografa e retorna a mensagem"""
        return decrypt_chat_message(self._encrypted_message)

    @message.setter
    def message(self, value):
        """Criptografa e armazena a mensagem"""
        self._encrypted_message = encrypt_chat_message(value)

    def set_message_plain(self, value):
        """Define mensagem sem criptografia (para migração)"""
        self._encrypted_message = value

    def get_preview(self, max_length=50):
        """Retorna prévia da mensagem descriptografada"""
        decrypted = self.message
        if len(decrypted) > max_length:
            return decrypted[:max_length] + "..."
        return decrypted

    def __repr__(self):
        return f'<Chat {self.id}: {self.get_preview()}>'
