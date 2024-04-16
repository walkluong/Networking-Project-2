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
                client_socket.send('@quit'.encode())
                client_program()
            
            elif message == "@quit": # If the client types 'quit', close the connection
                client_socket.send(message.encode())
                client_socket.close()
                os._exit(0) # instead of break, kills client
            
            elif message == "@help":
                print_options()
            
            else: #any non-client-command will be sent to the server to be handled
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
# starts the client and allows the to enter a server address and port number if they choose
def choose_server_and_port():
    print("\nDefault server address: 'localhost' \nDefault port: 12345 \nPress ENTER to accept defaults\n")
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
    
    while True:
        if username == '':
            username = input("Username can't be empty, enter a new username: ")
        else: 
            break
        
    client_socket.send(username.encode())
    
    while True:
        message = client_socket.recv(1024).decode()
        if message == "taken":
            username = input("USERNAME TAKEN, enter a new username: ")
            while True:
                if username == '':
                    username = input("Username can't be empty, enter a new username: ")
                else: 
                    break
            client_socket.send(username.encode())
        else: 
            break
    
    return username.upper().strip()

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

# prints all command options
def print_options():
    print("\nUse these commands as they appear (CASE SENSITIVE)")
    print("\nCOMMANDS: ")
    print("@connect: delete your current connection and allow you to reconnect to a new server and port")
    print("@users: list all users and their groups if the user shares at least 1 group with you")
    print("@message #: retrieves a message from the server with the matching ID (#)")
    print("@join: joins the public group and removes you from all private groups")
    print("@quit: remove your connection from the server")
    
    print("@groups: retrieves a list of all groups that can be joined")
    print("@groupjoin #: allows you to join a new private group, replace '#' with the group you want to join")
    print("              This will remove you from the public group but you can belong to multiple private groups")
    print("              Must join 1 group per command")
    print("@groupleave #: allows you to leave a group, replace '#' with the group you want to join")
    print("               you must always belong to at least 1 group")
    print("@grouppost # MSG: post a message to a message specific group (#) with a message (MSG)")
    print("@groupusers #: retrieve a list of users in the given group (#)")
    print("               You must belong to a group to see the users")
    print("@help: reprint these command options")
    print()


client_program()
