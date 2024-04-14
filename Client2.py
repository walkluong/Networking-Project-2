import socket
import threading
import os

prompt = "Enter your message: "

def client_program():
    
    # host IP and port number
    host = 'localhost'
    port = 12345
    
    # establish client socket and connect to server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    # choose public or private chat mode
    mode = choose_chat_mode(client_socket)

    # Ask user for username check for duplicates with server
    choose_username(client_socket)  

    # if user chose private chat mode
    if mode == "2":
        pick_group_id(client_socket)
    
    # start thread to continually check for incoming messages from server
    threading.Thread(target=receive_messages, args=(client_socket,)).start()
    # parent thread will continualy send user messages to server
    send_messages(client_socket)

# Gets user input and sends it to the server   
def send_messages(client_socket):
    while True:
        message = input(prompt) # Allow the client to send messages
        client_socket.send(message.encode())
        if message == "quit": # If the client types 'quit', close the connection
            # client_socket.send(message.encode())
            client_socket.close()
            os._exit(0) # instead of break, kills client

# constantly checks for incoming messages from server
def receive_messages(client_socket):
    print(client_socket.recv(1024).decode()) # handles different formatting of initial message
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print('\r{}\n{}'.format(message, prompt), end = '')
        except:
            print("\r\n\nYou have been disconnected.")
            print("\nIf you did not leave yourself, the server may have shut down.\n")
            os._exit(0) # instead of break, kills client


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

client_program()
