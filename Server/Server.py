import threading
import socket
import asyncio
import time
# global variable for time out of the server in sec

htmlSuccessStatusLine = 'HTTP/1.1 200 OK\r\n'
htmlNotFoundStatusLine = 'HTTP/1.1 404 Not Found\r\n'

   
# function for getting the file size
def getFileSize(file):
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    return size

# function for getting the value of a field in the req/resp
def getValueOfHeaderField(header, field):
    headerArray = header.split('\r\n')
    for h in headerArray:
        if (h.split()[0] == field + ':'): return h.split()[1]

# function of the work done by some connection on a separate thread
def startWork(server, channel, address):
    while True:
        # accepting the request and printing it
        reqest = channel.recv(1024).decode()
        print(reqest)

        reqestArray = reqest.split('\r\n', 1)
        requestLine = reqestArray[0]
        header = reqestArray[1]

        # parsing request Line
        method = requestLine.split()[0]
        filePath = requestLine.split()[1]

        #if GET request
        if (method == "GET"):
            fileContent = None

            #checking file extention
            extention = filePath.split('.')[1]

            # in case it is an image
            if (extention == 'png' or extention == 'jpg'):
                # check if the file exists
                try:
                    with open(filePath, 'rb') as file:
                        # reading the size of the image
                        fileSize = getFileSize(file)

                        # create the status line and header
                        resoponseHeader = 'content_length: ' + str(fileSize) + '\r\n' + 'content_type: image/' + extention + '\r\n'
                        channel.send((htmlSuccessStatusLine + resoponseHeader).encode())

                        #sending image in chunks in case it is larger than 1024 bytes
                        while (fileSize > 0):
                            fileContent = file.read(1024)
                            channel.send(fileContent)
                            fileSize = fileSize - 1024

                except(FileNotFoundError):
                    channel.send(htmlNotFoundStatusLine.encode())

            # in case it is a text file
            elif(extention == 'txt' or extention == 'html'):
                # check if the file exists
                try:
                    with open(filePath, 'r') as file:
                        # reading the size of the file
                        fileSize = getFileSize(file)

                        # create the status line and header
                        resoponseHeader = 'content_length: ' + str(fileSize) + '\r\n' + 'content_type: text/' + extention + '\r\n'
                        channel.send((htmlSuccessStatusLine + resoponseHeader).encode())

                        #sending image in chunks in case it is larger than 1024 bytes
                        while (fileSize > 0):
                            fileContent = file.read(1024)
                            channel.send(fileContent.encode())
                            fileSize = fileSize - 1024
                except(FileNotFoundError):
                    channel.send(htmlNotFoundStatusLine.encode())
           # in case it is another file type
            else:
                channel.send(htmlNotFoundStatusLine.encode()) 
        elif (method == "POST"):
            fileContent = reqest.split('\r\n\r\n', 1)[1]
            # To Do

     
# initializing the server socket for TCP handshaking
port = 8000
ip = '127.0.0.1'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, port))
# start listening for the incomming
server.listen(2)
print("Server started!")
beginingSwitch = True
while(True):
    
    try:
        newChannel, address = server.accept()
    except(socket.error):
        # print("Server closed due to time out (" , timeout , "sec)!")
        break

    
    print("new connection accepted: ", address)
    newChannelThread = threading.Thread(target= startWork, args= (server, newChannel, address))
    newChannelThread.start()
    
