import socket
import threading
from datetime import datetime, timezone, timedelta

from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import current_user
from app import db, users

chat = Blueprint('chat', __name__)
socketio = SocketIO()

typing_users = {} # empty Dictionary to keep track of typing users

@socketio.on('join', namespace='/chat')
def handle_join(data):
    if not current_user.is_authenticated:
        return emit('error', {'msg': 'User not authenticated.'})
    
    username = data['username']
    room = data['room']
    join_room(room)
    emit('message', {'msg': f'{username} has joined the room.'}, room=room)

@socketio.on('leave', namespace='/chat')
def handle_leave(data):
    if not current_user.is_authenticated:
        return emit('error', {'msg': 'User not authenticated.'})
    
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('message', {'msg': f'{username} has left the room.'}, room=room)

@socketio.on('send_message', namespace='/chat')
def handle_send_message(data):
    if not current_user.is_authenticated:
        return emit('error', {'msg': 'User not authenticated.'})
    
    room = data['room']
    message = data['message']
    username = current_user.username
    message_data = {
        'room': room,
        'username': username,
        'message': message,
        'sent_at': datetime.now(timezone.utc)
    }
    db.messages.insert_one(message_data)
    emit('message', {'msg': f'{username}: {message}'}, room=room)

@socketio.on('get_messages', namespace='/chat')
def handle_get_messages(data):
    if not current_user.is_authenticated:
        return emit('error', {'msg': 'User not authenticated.'})
    
    room = data['room']
    messages = db.messages.find({'room': room}).sort('sent_at', -1).limit(50)
    messages_list = []
    for message in messages:
        message['_id'] = str(message['_id'])
        message['sent_at'] = message['sent_at'].strftime('%Y-%m-%d %H:%M:%S')
        messages_list.append(message)
    emit('message_history', {'messages': messages_list}, room=room)

@socketio.on('delete_old_messages', namespace='/chat')
def delete_old_messages():
    """Delete messages older than 30 days."""
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    db.messages.delete_many({'sent_at': {'$lt': thirty_days_ago}})

@socketio.on('unsend_message', namespace='/chat')
def unsend_message(data):
    """Unsend a message from the chat."""
    if not current_user.is_authenticated:
        return emit('error', {'msg': 'User not authenticated.'})
    
    message_id = data['message_id']
    db.messages.delete_one({'_id': message_id})
    emit('message_deleted', {'msg': 'Message deleted successfully.'}, room=data['room'])

@socketio.on('broadcast_message', namespace='/chat')
def broadcast_message(data):
    """Broadcast a message to all users."""
    if not current_user.is_authenticated:
        return emit('error', {'msg': 'User not authenticated.'})
    
    message = data['message']
    socketio.emit('broadcast', {'msg': message}, namespace='/chat')

@socketio.on('typing', namespace='/chat')
def handle_typing(data):
    """Handle user typing indicator."""
    if not current_user.is_authenticated:
        return emit('error', {'msg': 'User not authenticated.'})
    
    room = data['room']
    username = current_user.username
    # Add user to the typing set
    if room not in typing_users:
        typing_users[room] = set()
    typing_users[room].add(username)
    # Emit updated list of typing users to the room
    emit('typing', {'users': list(typing_users[room])}, room=room)
    socketio.sleep(0.5)

@socketio.on('stop_typing', namespace='/chat')
def handle_stop_typing(data):
    """Handle when a user stops typing."""
    if not current_user.is_authenticated:
        return emit('error', {'msg': 'User not authenticated.'})
    
    room = data['room']
    username = current_user.username
    if room in typing_users:
        typing_users[room].discard(username)
        # Emit updated list of typing users to the room
        emit('typing', {'users': list(typing_users[room])}, room=room)
    
