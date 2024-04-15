import socket
import threading
import os

def client_program():
    
    client_socket = choose_server_and_port()
    
    # choose public or private chat mode
    mode = choose_chat_mode(client_socket)

    # Ask user for username check for duplicates with server
    username = choose_username(client_socket)  
    prompt = f"{username}: "

    # if user chose private chat mode
    if mode == "2":
        pick_group_id(client_socket)
    
    # start thread to continually check for incoming messages from server
    threading.Thread(target=receive_messages, args=(client_socket, prompt)).start()
    # parent thread will continualy send user messages to server
    send_messages(client_socket, prompt)

# Gets user input and sends it to the server   
def send_messages(client_socket, prompt):
    while True:
        message = input(prompt) # Allow the client to send messages
        
        if message:
            # calls function to choose new server and port
            if message == "@connect":
                client_socket.send('quit'.encode())
                client_program()
        
            # allows user to join a new group
            elif message.split(' ')[0] == "@join":
                client_socket.send(message.encode())
        
            # allows user to leave a group
            elif message.split(' ')[0] == "@leave":
                client_socket.send(message.encode())
            
            # gets all users in the users groups
            elif message == "@users":
                client_socket.send(message.encode())
            
            # gets a single message for the user
            elif message == "@message":
                pass
            
            elif message == "@quit": # If the client types 'quit', close the connection
                client_socket.send(message.encode())
                client_socket.close()
                os._exit(0) # instead of break, kills client
            
            elif message == "@help":
                print_options()
            
            else: #any non-command will be sent/broadcast as a normal message
                client_socket.send(message.encode())

# constantly checks for incoming messages from server
def receive_messages(client_socket, prompt):
    print(client_socket.recv(1024).decode()) # handles different formatting of initial message
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message == '@q':
                return
            elif message:
                print('\r{}\n{}'.format(message, prompt), end = '')
        except:
            print("\r\n\nYou have been disconnected.")
            print("\nIf you did not leave yourself, the server may have shut down.\n")
            os._exit(0) # instead of break, kills client

"""
HELPER FUNCTIONS
"""

def choose_server_and_port():
    print("Default server address: 'localhost' \nDefault port: 12345 \nPress ENTER to accept defaults\n")
    host = input("Enter server address: ")
    port = input("Enter port number: ")
    
    if host == '':
        host = 'localhost'
    if port == '':
        port = 12345
    
    server = (host, port)
    try:
        # establish client socket and connect to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server)
    except:
        print("\nCannot find server and port.\n")
        os._exit(0) # instead of break, kills client
        
    return client_socket

# Check for valid chat mode input and reprompt
def choose_chat_mode(client_socket):
    mode_choice = client_socket.recv(1024).decode()
    print(mode_choice)
    mode = input("\nEnter your choice of chat mode: ")
    
    while True:
        if (str(mode) == "1") or (str(mode) == "2"):
            break
        else: 
            mode = input("INVALID MODE, please enter your choice of [1] for Public or [2] for Private: ")
    
    client_socket.send(mode.encode())
    return mode

# If username is a duplicate on the server then reprompt
def choose_username(client_socket):
    
    username = input("\nEnter your username: ")
    client_socket.send(username.encode())
    
    while True:
        message = client_socket.recv(1024).decode()
        if message == "taken":
            username = input("USERNAME TAKEN, enter a new username: ")
            client_socket.send(username.encode())
        else: 
            break
    
    return username

# for mode 2: show availible groups and take user input, reprompt if necessary
def pick_group_id(client_socket):
    print("\nAvailable groups:")
    available_groups = client_socket.recv(1024).decode()
    print(available_groups)
    group_id = input("Enter group ID to join: ")
    while True:
        if (str(group_id) in ["1", "2", "3", "4", "5"]):
            break
        else: 
            group_id = input("INVALID GROUP ID, please enter valid group [1, 2, 3, 4, 5]: ")
    client_socket.send(group_id.encode())

def print_options():
    print("\nBegin your message with any of these commands (CASE SENSITIVE)")
    print("\nCOMMANDS: ")
    print("@connect: delete your current connection and allow you to reconnect to a new server and port")
    print("@users: list all users and their groups if the user shares at least 1 group with you")
    print("@join: allows you to join a new group, replace '#' with the group you want to join")
    print("         You can either belong to the single public message board")
    print("         or any one or more of the private message boards")
    print("@leave #: allows you to leave a group, replace '#' with the group you want to join")
    print("          you must always belong to at least 1 group")
    print("@quit: remove your connection from the server")
    
    print("@groupjoin #: allows you to join a new private group, replace '#' with the group you want to join")
    print("              This will remove you from the public group but you can belong to multiple private groups")
    print("              Must join 1 group at a time")
    print("@help: reprint these command options")
    print()


client_program()