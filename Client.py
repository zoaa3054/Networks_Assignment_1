import socket

# initializing the client connection
port = 8000
serverIP = "127.0.0.1"
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((serverIP, port))
print ("connection to server started successfuly")

while True: 
    message = input("you >> ")
    client.send(message.encode())
    respond = client.recv(1024).decode()
    print (serverIP, " >> ", respond)
    if respond.upper() == "CLOSED":
        client.close()
        break
    

