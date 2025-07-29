# Adicionar esta linha no main.py:
from app.routes.chat import chat_bp
app.register_blueprint(chat_bp, url_prefix='/chat')
