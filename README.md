# Networking-Project-2

# CONTRIBUTORS:

- **Clay Chilenski**
- **Quoc Luong**
- **Richard Roberts**


# IMPORTANT:

1. Users must have python installed on their computer, or have a developer environment with a python compiler.
    - **get python here**: https://www.python.org/

2. Users must have the** client.py** file downloaded into a known location on their computer.

3. Someone must have the **server.py** file downloaded into a known location on their computer.


# INSTRUCTIONS: 

## 1. The server host should run **server.py** on their computer

  - The host can either run the python code in an app like Visual Studio Code or can navigate to the directory of the **server.py** file in a terminal (macOS) or command prompt (win) and use 
    - python server.py

  - The default server address is set to 'localhost', to change to the hosts local IP, the host must replace 'localhost' with 'socket.gethostbyname(socket.gethostname())' on **server.py** line 5

## 2. All clients should run **client.py** on their computer

  - The client can either run the python code in an app like Visual Studio Code or can navigate to the directory of the **client.py** file in a terminal (macOS) or command prompt (win) and use 
    - python client.py

## 3. Follow the prompts in the command window of the running clinet.py file

  ### A. To join a host:

    i. If the server is running on the same machine, click enter twice to accept the default server address
    ii. If the sever is running on another machine, manually enter the server address in format 'a.b.c.d' 

    - The port number will depend on the hardcoded value on **server.py** line 6.
    - The server address and port number will print when **server.py** starts

  ### B. Choose a chat mode:

    [1] will put you into the public chat
        - Anyone else in the public chat can see your messages
        
    [2] will put put you into a private chat 
       - You will be prompted to choose a chat group, anyone in that chat group can see your messages
       - You can join new private chat groups and leave old ones later

  ### C. Enter a username:

    i. All usernames on the server are unique, you will be remprompted if your name is taken

  ### D. Read recent messages

    i. you will be able to see the 2 most recent messages sent to that group ID. 
    ii. Any time you join a new group you will see the 2 most recent messages

## 4. Send Messages:

    - 

# COMMANDS:

## Use these commands as they appear (CASE SENSITIVE)

| List of Client Commands | Description   |
| ----------------------- | ------------- |
| **@connect**            | delete your current connection and allow you to reconnect to a new server address and port number. |
| **@users**              | list all users that share a group and all their shared groups. |
| **@message #**          | retrieves a message from the server with the matching ID. |
| **@join**               | joins the public group and removes you from all private groups. |
| **@quit**               | remove your connection from the server |    
| **@groups**             | retrieves a list of all groups that can be joined |
| **@groupjoin #**        | allows you to join a new private group, replace '#' with the group you want to join. This will remove you from the public group but you can belong to multiple private groups. Must join 1 group per command |
| **@groupleave #**       | allows you to leave a group, replace '#' with the group you want to join. You must always belong to at least 1 group |
| **@grouppost # %**      | post a message to a message specific group (#) with a message (%) |
| **@groupusers #**       | retrieve a list of users in the given group (#). You must belong to a group to see the users |
| **@help**               | reprint these command options|


# ISSUES:

1. **Visual Bugs**
    - We realised it was difficult to process inputs while also using a prompt message before each users inputs. We did not fix all these issues

2. **Message Groups Changing**
    - We ran into many issues with messages, stored in tuples as (message, groups) where te groups would change for previously send messages when the sender would join a new group. This issue caused many different test cases to narrow down and eventually using breakpoints to discover what function and line were altering the previous messages. This issue was solved. 