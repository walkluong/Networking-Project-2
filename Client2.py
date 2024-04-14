import socket
import threading

def client_program():
    host = 'localhost'
    port = 12345
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    mode_choice = client_socket.recv(1024).decode()
    print(mode_choice)
    mode = input("Enter your choice (1 for Public, 2 for Private): ")
    client_socket.send(mode.encode())

    username = input("Enter your username: ")
    client_socket.send(username.encode())

    if mode == "2":
        available_groups = client_socket.recv(1024).decode()
        print(available_groups)
        group_id = input("Enter group ID to join: ")
        client_socket.send(group_id.encode())
    
    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    while True:
        message = input("Enter your message: ")
        if message == "quit":
            client_socket.send(b'')
            client_socket.close()
            break
        client_socket.send(message.encode())

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print(message)
        except:
            print("You have been disconnected.")
            break

client_program()
