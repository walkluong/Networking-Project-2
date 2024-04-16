import socket
import threading
import datetime

host = 'localhost'  # socket.gethostbyname(socket.gethostname())
port = 12345

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
                    
                elif message == '@groups':
                    get_groups(conn)
                
                elif message.split(' ')[0] == "@groupjoin":
                    new_group = message.split(' ')[1]
                    join_group(conn, new_group, group_IDs)
                
                elif message.split(' ')[0] == "@groupleave":
                    old_group = message.split(' ')[1]
                    leave_group(conn, old_group)
                
                elif message.split(' ')[0] == "@grouppost":
                    groupId = int(message.split(' ')[1])
                    groupMessage = ' '.join(message.split(' ')[2:])
                    post_group(conn, groupId, groupMessage, username)
                
                elif message == '@users':
                    get_users(conn, group_IDs, False)
                    
                elif message.split(' ')[0] == '@groupusers':
                    gid = int(message.split(' ')[1])
                    get_users(conn, [gid], True)

                elif message.split(' ')[0] == "@message":
                    id = message.split(' ')[1]
                    get_message(conn, id, group_IDs, all_messages)
                
                else:
                    formatted_message = f"[{len(all_messages)+1}, {username}, {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}"
                    all_messages.append((formatted_message, group_IDs))  # Store message with group_ids
                    broadcast(formatted_message, conn, group_IDs)
            else:
                remove(conn, username, group_IDs)
                print(f"Disconnected from {addr}")
                break
        except: # If something is wrong with the message, the code will just move to the next message
            continue

# send the message to all connections that also belong to one of the group_IDs
def broadcast(message, conn, group_IDs):
    for client in clients:
        if (client['conn'] != conn) and any(num in client['group_id_list'] for num in group_IDs):
            try:
                client['conn'].sendall(message.encode())
            except:
                remove(client['conn'], client['username'], client['group_id_list'])

# Send the last two messages from the history to a new client
def send_recent_messages(conn, group_id, messages):
    temp = []
    for msg in messages:
        if group_id in msg[1]: 
            temp.append(msg[0])
        
    if len(temp) == 0:
        conn.sendall("No recent messages".encode() + b'\n')
    else:
        for message in temp[-2:]:
            conn.sendall(message.encode() + b'\n')

# removes the client from the client list and closes the client socket
def remove(conn, username, group_IDs):
    for c in clients:
        if c['conn'] == conn:
            broadcast(f"{username} has left the server.", conn, group_IDs)
            clients.remove(c)
            c['conn'].close()
            break

# retrieves a single message by its message ID only if the user belongs to the group the message was sent in
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

# returns a list of group IDs for a users connection
def get_group_IDs(conn):
    for c in clients:
        if c['conn'] == conn:
            return c['group_id_list']

# puts the user into the public group and removes them from all private groups
def join_public(conn):
    for c in clients:
        if c['conn'] == conn:
            for gid in c['group_id_list']:
                broadcast(f"{c['username']} has left group {gid}.", c['conn'], [gid])
            c['group_id_list'] = [0]
            conn.send(f"You have joined the public group and left all private groups".encode())
            broadcast(f"{c['username']} has joined the public chat.", c['conn'], [0])
            send_recent_messages(conn, 0, all_messages)

# puts the user in group 'new_group' and removes them from the public chat if they were previously in it, notifies others
def join_group(conn, new_group, group_IDs):
    new_group = int(new_group)
    for c in clients:
        if c['conn'] == conn:
            if new_group not in c['group_id_list'] and new_group in [1, 2, 3, 4, 5]:
                
                new_IDs = group_IDs + [new_group]             
                if 0 in new_IDs: 
                    broadcast(f"{c['username']} has left the public chat.", c['conn'], [0])
                    new_IDs.remove(0)
                c['group_id_list'] = new_IDs
                    
                conn.send(f"You have joined group {new_group}, you may no longer be in group 0".encode())
                broadcast(f"{c['username']} has joined group {new_group}.", c['conn'], [new_group])
                send_recent_messages(conn, new_group, all_messages)
            elif new_group not in [1, 2, 3, 4, 5]: 
                conn.send(f"Group {new_group} doesn't exist".encode())
            else:
                conn.send(f"Already in group {new_group}".encode())
            return

# removes a user from a group and notifies others in that group
def leave_group(conn, old_group):
    old_group = int(old_group)
    for c in clients:
        if c['conn'] == conn:
            if len(c['group_id_list']) <= 1:
                conn.send("You must belong to at least one group at all times".encode())
            elif old_group in c['group_id_list']:
                c['group_id_list'].remove(old_group)
                conn.send(f"You have left group {old_group}".encode())
                broadcast(f"{c['username']} has left group {old_group}.", c['conn'], [old_group])
            else:
                conn.send(f"Your not in group {old_group} or it may not exist".encode())
            return

# gets a list of all users that share a group ID with the user, or gets all users in a specific group
def get_users(conn, group_IDs, justGroupUsers):
    users = []
    
    if justGroupUsers:
        if group_IDs[0] in get_group_IDs(conn):
            for client in clients:
                if any(num in client['group_id_list'] for num in group_IDs):
                    users.append((client['username'], set(client['group_id_list']).intersection(group_IDs)))
        elif group_IDs[0] not in [1,2,3,4,5]:
            conn.send(f"Group {group_IDs[0]} does not exist".encode())
        else:
            conn.send(f"Must join {group_IDs[0]} to see users".encode())
    
    else: 
        for client in clients:
            if any(num in client['group_id_list'] for num in group_IDs):
                users.append((client['username'], set(client['group_id_list']).intersection(group_IDs)))
    
    conn.send(str(users).encode())

# gets all private groups and sends them to the client
def get_groups(conn):
    conn.sendall("\n".join([f"{id}: {name}" for id, name in groups.items()]).encode())

# sends a mesage to only a specified groupId
def post_group(conn, groupId, groupMessage, username):
    if groupId in [1,2,3,4,5]: 
        if groupId in get_group_IDs(conn):
            formatted_message = f"[{len(all_messages)+1}, {username}, {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {groupMessage}"
            all_messages.append((formatted_message, [groupId]))  # Store message with group_ids
            broadcast(formatted_message, conn, [groupId])
        else: 
            conn.send(f"Can't send to {groupId} without joining".encode())
    else:
        conn.send(f"Group {groupId} doesn't exsist".encode())

# Check for duplicate usernames
def check_username(conn):
    username = conn.recv(1024).decode().upper().strip()  # Get username at the beginning for both modes.

    while any(c['username'] == username for c in clients): # NO DUPLICATES on entire server
        conn.send("taken".encode())
        username = conn.recv(1024).decode().upper().strip()
        
    conn.send("valid".encode())
    return username

# initializes a client in the public chat
def public_chat(conn, username):
    welcome_message = f"{username} has joined the public chat."
    group_IDs = [0]
    return create_client(conn, username, group_IDs, welcome_message)

# initializes a client in a private chat
def private_chat(conn, username):
    get_groups(conn)
    group_IDs = []
    group_IDs.append(int(conn.recv(1024).decode()))
    group_name = groups[group_IDs[0]]
    welcome_message = f"{username} has joined {group_name}."
    
    return create_client(conn, username, group_IDs, welcome_message)

# adds a client/user to the client list
def create_client(conn, username, group_IDs, welcome_message):
    clients.append({'conn': conn, 'username': username, 'group_id_list': group_IDs})
    broadcast(welcome_message, conn, group_IDs)
    send_recent_messages(conn, group_IDs[0], all_messages)
    
    return group_IDs

# create the listening socket and loop to accept all new incoming client connections
def start_server():
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
