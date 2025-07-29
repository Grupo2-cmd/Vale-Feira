"""
Rotas de chat
"""
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, desc
from app import db
from app.models.chat import Chat
from app.models.product import Product
from app.models.user import User
from app.forms.chat import ChatForm

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/<int:product_id>/<int:other_user_id>', methods=['GET', 'POST'])
@login_required
def chat(product_id, other_user_id):
    """Chat entre dois usuários específicos sobre um produto"""
    product = Product.query.get_or_404(product_id)
    other_user = User.query.get_or_404(other_user_id)

    # Verificações de segurança
    if current_user.id == other_user.id:
        flash('Você não pode conversar consigo mesmo', 'error')
        return redirect(url_for('product.product_detail', id=product_id))

    # Verificar permissão
    if current_user.id != product.seller_id and other_user.id != product.seller_id:
        flash('Pelo menos um usuário deve ser o vendedor do produto', 'error')
        return redirect(url_for('product.product_detail', id=product_id))

    form = ChatForm()

    if form.validate_on_submit():
        chat_message = Chat(
            product_id=product_id,
            sender_id=current_user.id,
            receiver_id=other_user_id
        )
        chat_message.message = form.message.data  # Criptografa automaticamente

        db.session.add(chat_message)
        db.session.commit()

        flash('Mensagem enviada com sucesso!', 'success')
        return redirect(url_for('chat.chat', product_id=product_id, other_user_id=other_user_id))

    # Buscar mensagens entre os usuários
    chats = Chat.query.filter(
        and_(
            Chat.product_id == product_id,
            or_(
                and_(Chat.sender_id == current_user.id, Chat.receiver_id == other_user_id),
                and_(Chat.sender_id == other_user_id, Chat.receiver_id == current_user.id)
            )
        )
    ).order_by(Chat.created_at.asc()).all()

    # Marcar mensagens como lidas
    Chat.query.filter(
        and_(
            Chat.product_id == product_id,
            Chat.sender_id == other_user_id,
            Chat.receiver_id == current_user.id,
            Chat.is_read == False
        )
    ).update({'is_read': True})
    db.session.commit()

    return render_template('chat.html',
                         form=form,
                         chats=chats,
                         product=product,
                         other_user=other_user)

@chat_bp.route('/my_chats')
@login_required
def my_chats():
    """Mostra todas as conversas do usuário agrupadas por parceiro"""
    all_chats = Chat.query.filter(
        or_(Chat.sender_id == current_user.id, Chat.receiver_id == current_user.id)
    ).order_by(desc(Chat.created_at)).all()

    # Agrupar conversas por produto e parceiro
    chat_groups = {}
    for chat in all_chats:
        other_user_id = chat.receiver_id if chat.sender_id == current_user.id else chat.sender_id
        key = f"{chat.product_id}_{other_user_id}"

        if key not in chat_groups:
            chat_groups[key] = {
                'product': chat.product,
                'other_user': User.query.get(other_user_id),
                'latest_chat': chat,
                'unread_count': 0
            }

        if chat.receiver_id == current_user.id and not chat.is_read:
            chat_groups[key]['unread_count'] += 1

    chat_groups_list = list(chat_groups.values())
    chat_groups_list.sort(key=lambda x: x['latest_chat'].created_at, reverse=True)

    return render_template('my_chats.html', chat_groups=chat_groups_list)
