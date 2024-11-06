import socket

# function for getting the value of a field in the req/resp
def getValueOfHeaderField(header, field):
    headerArray = header.split('\r\n')
    for h in headerArray:
        if (h.split()[0] == field + ':'): return h.split()[1]

# initializing the client connection
port = 8000
serverIP = "127.0.0.1"
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((serverIP, port))
print ("connection to server started successfuly")

while True: 
    message = input("you >> ")
    message = message.replace('\\r\\n', '\r\n')
    #checking if server is closed
    try:
        # attaching host header
        message = message + '\r\nhost: ' + serverIP + ":" + str(port)
        client.send(message.encode())
        method = message.split()[0]
        filePath = message.split()[1]
        response = client.recv(1024).decode()
        print(response)
        respondArray = response.split('\r\n', 1)
        statusLine = respondArray[0]
        #in case of GET a file is saved in the current directory if file is found in the server
        if (method == "GET"):                
            # if file requested is found in the server (check status line)
            if (statusLine == 'HTTP/1.1 200 OK'): 
                fileType = getValueOfHeaderField(respondArray[1], 'content_type')
                fileSize = int(getValueOfHeaderField(respondArray[1], 'content_length'))
                # in case it is an image
                if (fileType == 'image/png' or fileType == 'image/jpg'):
                    with open(filePath, 'wb') as image:
                        # loop on image size for accepting all image chunks
                        while (fileSize > 0):
                            response = client.recv(1024)
                            image.write(response)
                            print(response)
                            fileSize = fileSize - 1024

                # in case it is a text file   
                elif (fileType == 'text/txt' or fileType == 'text/html'):    
                    with open(filePath, 'w') as file:
                        while(fileSize > 0):
                            response = client.recv(1024).decode()
                            file.write(response)
                            print(response)
                            fileSize = fileSize - 1024

        # elif (method == 'POST'):
            # TO DO
    except(ConnectionAbortedError, ConnectionResetError):
        print("Server is closed!")
        client.close()
        break
    
    

