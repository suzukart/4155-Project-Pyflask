import socket
import threading

HOST = '127.0.0.1'  # Use localhost for testing
PORT = 8081  # Open port for the server

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []  # List of connected client sockets
usernames = {}  # Dictionary mapping client sockets to usernames


def broadcast(message, sender=None):
    """Send a message to all clients except the sender."""
    for client in clients:
        # You can decide whether to send back to the sender as well.
        if client != sender:
            try:
                client.send(message)
            except Exception as e:
                print("Error broadcasting message:", e)
                remove_client(client)


def remove_client(client):
    """Remove a client from the list and the username dictionary."""
    if client in clients:
        clients.remove(client)
    if client in usernames:
        username = usernames[client]
        del usernames[client]
        leave_message = f"{username} has left the chat.".encode('utf-8')
        broadcast(leave_message)


def handle_client(client):
    """Handles a client connection, including username registration and message broadcasting."""
    try:
        # First message should be the username.
        username = client.recv(1024).decode('utf-8')
        usernames[client] = username
        welcome_message = f"{username} has joined the chat!".encode('utf-8')
        broadcast(welcome_message, sender=client)

        while True:
            message = client.recv(1024)
            if message:
                # Prepend the username to the received message.
                formatted_message = f"{username}: {message.decode('utf-8')}".encode('utf-8')
                broadcast(formatted_message, sender=client)
            else:
                remove_client(client)
                client.close()
                break
    except Exception as e:
        print("Error handling client:", e)
        remove_client(client)
        client.close()


def receive_connections():
    print(f"Server listening on {HOST}:{PORT}...")
    while True:
        client, address = server.accept()
        print(f"New connection from {address}")
        clients.append(client)
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    receive_connections()