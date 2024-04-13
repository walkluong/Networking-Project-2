import socket
import threading
import os

prompt = "Enter your message: "

def client_program(): # Create a client socket and connect to the server
    host = 'localhost'
    port = 12345
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    username = input("Enter your username: ") # Get username input from the client and send it to the server      
    client_socket.send(username.encode())
    
    # if username is a duplicate then reprompt
    while True:
        message = client_socket.recv(1024).decode()
        if message == "taken":
            username = input("Username taken, enter a new username: ")
            client_socket.send(username.encode())
        else: 
            break
    
    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    while True:
        message = input(prompt) # Allow the client to send messages
        client_socket.send(message.encode())
        if message == "quit": # If the client types 'quit', close the connection
            client_socket.send(message.encode())
            client_socket.close()
            os._exit(0) # instead of break, kills client

def receive_messages(client_socket): # Continuously receive and print messages from the server
    
    print(client_socket.recv(1024).decode()) # handles different formatting of initial message
    while True: 
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print('\r{}\n{}'.format(message, prompt), end = '')
        except:
            print("\r\nYou have been disconnected.")
            os._exit(0) # instead of break, kills client

client_program()

# Personal\GitHub\Networking-Project-2