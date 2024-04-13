import socket
import threading


def client_program(): # Create a client socket and connect to the server
    host = 'localhost'
    port = 12345
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    username = input("Enter your username: ") # Get username input from the client and send it to the server
    client_socket.send(username.encode())
    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    while True:
        message = input("Enter your message: ") # Allow the client to send messages
        if message == "quit": # If the client types 'quit', close the connection
            client_socket.send(b'')
            client_socket.close()
            break
        client_socket.send(message.encode())

def receive_messages(client_socket): # Continuously receive and print messages from the server
    while True: 
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print(message)
        except:
            print("You have been disconnected.")
            break

client_program()
