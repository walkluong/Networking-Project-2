import socket
import threading
import datetime

# Define groups for private chat
groups = {1: "Group A", 2: "Group B", 3: "Group C", 4: "Group D", 5: "Group E"}
clients = []  # List to keep track of connected clients
messages = []  # List to store messages

def client_thread(conn, addr):
    conn.sendall("Choose chat mode: 1 for Public, 2 for Private".encode())
    mode = conn.recv(1024).decode()
    username = conn.recv(1024).decode()  # Get username at the beginning for both modes.

    # Handle public chat mode
    if mode == "1":  # Public chat
        # Check for duplicate usernames
        while any(c['username'] == username for c in clients if c['group_id'] == 0):
            conn.send("taken".encode())
            username = conn.recv(1024).decode()
        conn.send("Valid username!".encode())

        group_id = 0  # Zero indicates the public group
        welcome_message = f"{username} has joined the public chat."
        clients.append({'conn': conn, 'username': username, 'group_id': group_id})
        broadcast(welcome_message, username, group_id)
        send_recent_messages(conn, group_id)
    else:  # Private chat
        conn.sendall("Available groups:\n" + "\n".join([f"{id}: {name}" for id, name in groups.items()]).encode())
        group_id = int(conn.recv(1024).decode())
        group_name = groups[group_id]
        welcome_message = f"{username} has joined {group_name}."
        clients.append({'conn': conn, 'username': username, 'group_id': group_id})
        broadcast(welcome_message, username, group_id)
        send_recent_messages(conn, group_id)

    # Common message receiving loop
    while True:
        try:
            message = conn.recv(1024).decode()
            if message == 'quit':
                remove(conn, username, group_id)
                broadcast(f"{username} has left the chat.", username, group_id)
                break
            elif message:
                formatted_message = f"{len(messages)+1}, {username}, {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, {message}"
                messages.append((formatted_message, group_id))  # Store message with group_id
                broadcast(formatted_message, username, group_id)
            else:
                remove(conn, username, group_id)
                break
        except:
            continue

def broadcast(message, sender, group_id):
    for client in clients:
        if client['username'] != sender and client['group_id'] == group_id:
            try:
                client['conn'].sendall(message.encode())
            except:
                remove(client['conn'], client['username'], client['group_id'])

def send_recent_messages(conn, group_id):
    # Send the last two messages from the history to a new client
    relevant_messages = [msg for msg, gid in messages if gid == group_id]
    if not relevant_messages:
        conn.sendall("No recent messages".encode() + b'\n')
    else:
        for message in relevant_messages[-2:]:
            conn.sendall(message.encode() + b'\n')

def remove(conn, username, group_id):
    for i, client in enumerate(clients):
        if client['conn'] == conn:
            conn.close()
            clients.pop(i)
            broadcast(f"{username} has left the chat.", username, group_id)
            break

def start_server():
    host = 'localhost'
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server is listening on [{server_socket.getsockname()}]")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connected to {addr}")
        threading.Thread(target=client_thread, args=(conn, addr)).start()

start_server()
