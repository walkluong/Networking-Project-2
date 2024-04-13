import socket
import threading
import datetime

clients = [] # List to keep track of connected clients
messages = [] # List to store messages

def client_thread(conn, addr):
    username = conn.recv(1024).decode() # Receive the username from the client

    # Check for duplicate usernames
    while [item for item in clients if item[1] == username]:
        conn.send("taken".encode())
        username = conn.recv(1024).decode()
    conn.send("Valid username!".encode())
    
    welcome_message = f"{username} has joined the chat."
    broadcast(welcome_message, "") # Notify all clients that a new user has joined
    
    # Create a tuple for each connection and username to more easily handle clients in loops
    client_ID = (conn, username)
    
    clients.append(client_ID) # Add new client/user to the group
    send_recent_messages(conn) # Send the last two messages to the new client

    while True:
        try:
            message = conn.recv(1024).decode() #make sure the message is normal, otherwise will skip the loop, and move to the next one.
            if message == 'quit':
                remove(client_ID)
                broadcast(f"{username} has left the chat.", "")
                break
            elif message: # If message is normal, format the message as:  “Message ID, Sender, Post Date, Subject"
                formatted_message = f"{len(messages)+1}, {username}, {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, {message}"
                messages.append(formatted_message) # Store message into the list
                broadcast(formatted_message, username) #send message to all clients in the group
            else:
                remove(client_ID)
                break
        except: # If something is wrong with the message, the code will just move to the next message
            continue

def broadcast(message, sender): # Send a message to all connected clients except the sender
    for c in clients:
        if c[1] != sender:
            c[0].sendall(message.encode())

def send_recent_messages(conn): # Send the last two messages from the history to a new client
    if len(messages) == 0:
        conn.sendall("No recent messages".encode() + b'\n')
    else:
        for message in messages[-2:]:
            conn.sendall(message.encode() + b'\n')

def remove(client_ID): # Remove a client that has disconnected and notify others
    for c in clients:
        if c == client_ID:
            c[0].close()
            clients.remove(c)
            break

def start_server(): # Create a socket and bind it to a host and port
    host = 'localhost'
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    print(f"Server is listening on [{server_socket.getsockname()}, Port: {port}]")

    while True:
        conn, addr = server_socket.accept() # Accept new connections
        print(f"Connected to {addr}")
        threading.Thread(target=client_thread, args=(conn, addr)).start() # Start a new thread for each connected client


start_server()
