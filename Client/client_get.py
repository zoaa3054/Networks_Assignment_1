import socket
import sys

# function for getting the value of a field in the req/resp
def getValueOfHeaderField(header, field):
    headerArray = header.split('\r\n')
    for h in headerArray:
        if (h.split()[0] == field + ':'): return h.split()[1]
    return None

def detach0x89(encoding):
    res = b''
    for byte in encoding:
        if byte == 0x89:
            res += byte
    return res
# initializing the client connection
# to run the client get http request write the following
# py client_get file-path host-name (port)

port = 80 # defaul port number for http
serverIP = None
filePath = None
# in case port is not passed
if (len(sys.argv) == 3):
    filePath = sys.argv[1]
    serverIP = sys.argv[2]
# in case port is passed
if (len(sys.argv) == 4):
    filePath = sys.argv[1]
    serverIP = sys.argv[2]
    port = int(sys.argv[3])

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((serverIP, port))
print ("connection to server started successfuly")

while True: 
    #checking if server is closed
    try:
        # attaching host header
        request = f"GET {filePath} HTTP/1.1\r\nAccept: */*\r\nCache-Control: no-cache\r\nHost: {serverIP}:{port}\r\nAccept-Encoding: gzip, deflate, br\r\nConnection: keep-alive\r\n"
        client.send(request.encode())
        response = client.recv(3072).decode()
        print(response)
        respondArray = response.split('\r\n', 1)
        statusLine = respondArray[0]
        header = respondArray[1].split('\r\n\r\n')[0]
        # in case of GET a file is saved in the current directory if file is found in the server               
        # if file requested is found in the server (check status line)
        if (statusLine == 'HTTP/1.1 200 OK'): 
            fileType = getValueOfHeaderField(header, 'Content-Type')
            if (filePath[0] == '/'): filePath = '.' + filePath
            checkChuncked = True
            if (getValueOfHeaderField(header, 'Transfer-Encoding') == None): 
                checkChuncked = False
            # in case it is an image
            if (fileType == 'image/png' or fileType == 'image/jpg'):
                if (checkChuncked):
                    with open(filePath, 'wb') as image:
                        body = None
                        chunk = 1
                        # loop on image size for accepting all image chunks
                        body = client.recv(3072)
                        while (body != b'0\r\n\r\n'):
                            image.write((body))
                            print("chunk number: ", chunk, "\n", body)
                            chunk += 1
                            body = client.recv(3072)
                else:
                    with open(filePath, 'wb') as image:
                        body = respondArray[1].split('\r\n\r\n')[1].encode()
                        image.write((body))
            # in case it is a text file   
            elif (fileType == 'text/txt' or fileType == 'text/html'):    
                if (checkChuncked):
                    with open(filePath, 'w') as file:
                        body = None
                        chunk = 1
                        while(body != '0\r\n\r\n'):
                            body = client.recv(3072).decode()
                            file.write(body)
                            print("chunk number: ", chunk, "\n", body)
                            chunk += 1
                else:
                    with open(filePath, 'w') as file:
                        body = respondArray[1].split('\r\n\r\n')[1]
                        file.write(body)

    except(ConnectionAbortedError, ConnectionResetError):
        print("Server is closed!")
        client.close()
        break
    
    client.close()
    break

