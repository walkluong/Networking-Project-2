import socket
import threading
import datetime

# Define groups for private chat
groups = {1: "Group 1", 2: "Group 2", 3: "Group 3", 4: "Group 4", 5: "Group 5"}
clients = []  # List to keep track of connected clients
all_messages = []  # List to store messages

def client_thread(conn, addr):
    
    conn.sendall("\nChoose chat mode: 1 for Public, 2 for Private".encode())
    mode = conn.recv(1024).decode()

    # Check for duplicate usernames
    username = check_username(conn)

    # Handle public chat mode
    if mode == "1":  # Public chat
        group_IDs = public_chat(conn, username)

    # Handle private chat mode
    else:  # Private chat
        group_IDs = private_chat(conn, username)

    # Common message receiving loop
    while True:
        try:
            group_IDs = get_group_IDs(conn)
            message = conn.recv(1024).decode()
            if message:
                if message == '@quit':
                    conn.send('@q'.encode())
                    remove(conn, username, group_IDs)
                    print(f"Disconnected from {addr}")
                    break
                
                elif message == '@join':
                    join_public(conn)
                
                elif message.split(' ')[0] == "@groupjoin":
                    new_group = message.split(' ')[1]
                    join_group(conn, new_group, group_IDs)
                
                elif message.split(' ')[0] == "@leave":
                    old_group = message.split(' ')[1]
                    leave_group(conn, old_group)
                
                elif message == '@users':
                    user_list = get_users(group_IDs)
                    conn.send(str(user_list).encode())

                elif message.split(' ')[0] == "@message":
                    id = message.split(' ')[1]
                    get_message(conn, id, group_IDs, all_messages)
                
                else:
                    formatted_message = f"[{len(all_messages)+1}, {username}, {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
                    all_messages.append((formatted_message, group_IDs))  # Store message with group_ids
                    broadcast(formatted_message, username, group_IDs)
            else:
                remove(conn, username, group_IDs)
                print(f"Disconnected from {addr}")
                break
        except: # If something is wrong with the message, the code will just move to the next message
            continue


def broadcast(message, sender, group_IDs):
    for client in clients:
        if (client['username'] != sender) and any(num in client['group_id_list'] for num in group_IDs):
            try:
                client['conn'].sendall(message.encode())
            except:
                remove(client['conn'], client['username'], client['group_id_list'])


def send_recent_messages(conn, group_id, messages):
    # Send the last two messages from the history to a new client
    #relevant_messages = [msg for msg in messages if group_id in msg[1]]
    temp = []
    for msg in messages:
        if group_id in msg[1]: 
            temp.append(msg[0])
        
    if len(temp) == 0:
        conn.sendall("No recent messages".encode() + b'\n')
    else:
        for message in temp[-2:]:
            conn.sendall(message.encode() + b'\n')


def remove(conn, username, group_IDs):
    for c in clients:
        if c['conn'] == conn:
            broadcast(f"{username} has left the server.", username, group_IDs)
            clients.remove(c)
            c['conn'].close()
            break


def get_message(conn, id, group_IDs, messages):
    if id.isdigit():
        if int(id) > len(messages):
            conn.sendall(f"Message {id} does not exist".encode())
        for msg in messages:
            temp = msg[0]
            if int(temp.replace(temp[0], "", 1).split(',')[0]) == int(id):
                if any(num in msg[1] for num in group_IDs):
                    conn.sendall(msg[0].encode() + b'\n')
                else:
                    conn.sendall(f"Message {id} was sent to a group you're not in.".encode())
                return
    else: 
        conn.sendall(f"{id} is not a valid message id!".encode())

def get_group_IDs(conn):
    for c in clients:
        if c['conn'] == conn:
            return c['group_id_list']


def join_public(conn):
    for c in clients:
        if c['conn'] == conn:
            c['group_id_list'] = [0]
            conn.send(f"You have joined the public group and left all private groups".encode())
            broadcast(f"{c['username']} has joined the public chat.", c['username'], c['group_id_list'])
            send_recent_messages(conn, 0, all_messages)

def join_group(conn, new_group, group_IDs):
    new_group = int(new_group)
    for c in clients:
        if c['conn'] == conn:
            if new_group not in c['group_id_list'] and new_group in [1, 2, 3, 4, 5]:
                
                new_IDs = group_IDs + [new_group]             
                if 0 in new_IDs: 
                    new_IDs.remove(0)
                c['group_id_list'] = new_IDs
                    
                conn.send(f"You have joined group {new_group}, you may no longer be in group 0".encode())
                broadcast(f"{c['username']} has joined group {new_group}.", c['username'], c['group_id_list'])
                send_recent_messages(conn, new_group, all_messages)
            elif new_group not in [1, 2, 3, 4, 5]: 
                conn.send(f"Group {new_group} doesn't exist".encode())
            else:
                conn.send(f"Already in group {new_group}".encode())
            return


def leave_group(conn, old_group):
    old_group = int(old_group)
    for c in clients:
        if c['conn'] == conn:
            if len(c['group_id_list']) <= 1:
                conn.send("You must belong to at least one group at all times".encode())
            elif old_group in c['group_id_list']:
                c['group_id_list'].remove(old_group)
                conn.send(f"You have left group {old_group}".encode())
                broadcast(f"{c['username']} has left group {old_group}.", c['username'], c['group_id_list'])
            else:
                conn.send(f"Your not in group {old_group} or it may not exist".encode())
            return

def get_users(group_IDs):
    users = []
    for client in clients:
        if any(num in client['group_id_list'] for num in group_IDs):
            users.append((client['username'], set(client['group_id_list']).intersection(group_IDs)))
    
    return users


def check_username(conn):
    username = conn.recv(1024).decode()  # Get username at the beginning for both modes.
    
    # Check for duplicate usernames
    while any(c['username'] == username for c in clients): # NO DUPLICATES on entire server
        conn.send("taken".encode())
        username = conn.recv(1024).decode()
        
    conn.send("valid".encode())
    return username


def public_chat(conn, username):
    welcome_message = f"{username} has joined the public chat."
    group_IDs = [0]
    return create_client(conn, username, group_IDs, welcome_message)


def private_chat(conn, username):
    conn.sendall("\n".join([f"{id}: {name}" for id, name in groups.items()]).encode())
    group_IDs = []
    group_IDs.append(int(conn.recv(1024).decode()))
    group_name = groups[group_IDs[0]]
    welcome_message = f"{username} has joined {group_name}."
    
    return create_client(conn, username, group_IDs, welcome_message)


def create_client(conn, username, group_IDs, welcome_message):
    clients.append({'conn': conn, 'username': username, 'group_id_list': group_IDs})
    broadcast(welcome_message, username, group_IDs)
    send_recent_messages(conn, group_IDs[0], all_messages)
    
    return group_IDs


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