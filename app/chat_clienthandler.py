import socket
import threading

from flask_login import current_user
from bson import ObjectId

from app import users

HOST = '127.0.0.1'  # Server IP (localhost for testing)
PORT = 8081         # The server's port

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

user_data = users.get_collection('users').find_one({"_id": ObjectId(current_user.get_id())})
username = user_data.get('username', 'Guest')
client.send(username.encode('utf-8'))

def receive_messages():
    """Continuously listen for messages from the server and display them."""
    while True:
        try:
            message = client.recv(1024)
            if message:
                print(message.decode('utf-8'))
            else:
                break  # Server closed connection
        except Exception as e:
            print("Error receiving message:", e)
            break

def send_messages():
    """Continuously send user input to the server."""
    while True:
        message = input('')
        if message:
            client.send(message.encode('utf-8'))

# Start the thread to listen for messages.
receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

# Main thread handles sending messages.
send_messages()