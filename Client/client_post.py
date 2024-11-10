import socket
import sys

# function for getting the value of a field in the req/resp
def getValueOfHeaderField(header, field):
    headerArray = header.split('\r\n')
    for h in headerArray:
        if (h.split()[0] == field + ':'): return h.split()[1]
    return None

def get_file_size(file):
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    return size


def handle_post_text_file_request(url):
    """
    Handles an HTTP GET request for a text file and returns a response string.
    
    Args:
        url (str): The URL of the requested text file.

    Returns:
        list: A list of byte-encoded strings representing the HTTP response.
    """
    file_extension = url.split('.')[-1]
    # Default to 'txt' if the extension is 'htm'
    if file_extension == 'htm':
        file_extension = 'txt'

    response_body = None
    try:
        with open(url, 'r') as file:
            file_size = get_file_size(file)
            # Read the entire file if its size is less than 512 bytes
            if file_size < 3000:
                response_body = file.read()
    except FileNotFoundError:
        # Return a 404 Not Found response if the file is not found
        print('Error 404: File Not Found')
        return None

    # If the file size is small, send it as a single response
    if file_size < 3000:
        return [
            'POST {url} HTTP/1.1\r\nContent-Type: text/{file_extension}\r\nContent-Length: {file_size}\r\nConnection: keep-alive\r\n\r\n{response_body}'
            .format(
                url=url,
                response_body=response_body,
                file_size=file_size,
                file_extension=file_extension,
            )
            .encode()
        ]
    else:
        # Use chunked transfer encoding for larger files
        response = []
        response.append(
            'POST {url} HTTP/1.1\r\nContent-Type: text/{file_extension}\r\nTransfer-Encoding: chunked\r\nConnection: keep-alive\r\n\r\n'
            .format(url=url, file_extension=file_extension)
            .encode()
        )

        # Read and send the file in chunks of 3000 bytes
        with open(url, 'r') as file:
            while file_size > 0:
                file_content = file.read(3000)
                size = str(hex(len(file_content))).replace("0x",'')
                response.append('{size}\r\n{content}\r\n'.format(size=size,content=file_content).encode())
                file_size -= 3000


        # Indicate the end of the chunked transfer
        response.append(b'0\r\n\r\n')
        return response

def handle_post_image_request(url):
    """
    Handles an HTTP GET request for an image and returns a response string.

    Args:
        url (str): The URL of the requested image file.

    Returns:
        list: A list of byte-encoded strings representing the HTTP response.
    """
    file_size = 0
    extension = url.split('.')[-1]

    # Default to 'avif' if the extension is 'ico' or 'icon'
    if extension == 'ico' or extension == 'icon':
        extension = 'avif'

    try:
        with open(url, 'rb') as file:
            file_size = get_file_size(file)
    except FileNotFoundError:
        # Return a 404 Not Found response if the file is not found
        print("Error 404: File Not Found")
        return None

    # If the file size is small, send it as a single response
    if file_size < 3000:
        with open(url, 'rb') as file:
            response_body = file.read()
        return [
            "POST {url} HTTP/1.1\r\nContent-Type: image/{extension}\r\nContent-Length: {size}\r\nConnection: keep-alive\r\n\r\n"
            .format(url=url, size=file_size, extension=extension)
            .encode()
            + response_body + '\r\n'.encode()
        ]

    # Use chunked transfer encoding for larger files
    response = []
    response.append(
        "POST {url} HTTP/1.1\r\nContent-Type: image/{extension}\r\nTransfer-Encoding: chunked\r\nConnection: keep-alive\r\n\r\n"
        .format(url=url, extension=extension)
        .encode()
    )

    # Read and send the file in chunks of 1024 bytes
    with open(url, 'rb') as file:
        while file_size > 0:
            file_content = file.read(3000)
            size = str(hex(len(file_content))).replace("0x",'')
            msg= size.encode() + '\r\n'.encode() + file_content + "\r\n".encode()
            response.append(msg)
            file_size -= len(file_content)

    # Indicate the end of the chunked transfer
    response.append('0\r\n\r\n'.encode())
    return response
def handle_post_request(url):
    """Handles an HTTP GET request and returns a response string.

    The request is handled according to the Accept header of the request.
    If the header contains 'text', the request is handled as a request
    for a text file. If the header contains 'image', the request is
    handled as a request for an image.

    Parameters:
        method (str): The method of the request.
        url (str): The requested URL.
        version (str): The HTTP version of the request.
        headers (dict): The headers of the request.

    Returns:
        list: A list of byte strings representing the HTTP response.
    """


    if url == '/':
        url = '/index.html'

    
    extension = url.split('.')[-1]
    if extension == 'htm' or extension == 'html' or extension == 'txt':
        if list(url)[0] == '/':
            return handle_post_text_file_request('.' + url) 
        else:
            return handle_post_text_file_request(url)
    
    if extension == 'png' or extension == 'gif' or extension == 'jpg' or extension == 'jpeg' or extension == 'ico' or extension == 'icon':
        if list(url)[0] == '/':
            return handle_post_image_request('.' + url) 
        else:
                return handle_post_image_request(url)
            

    print("Error 404: File Not Found")
    return None

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
        headers={
            'Accept': '*/*',
            'Cache-Control': 'no-cache',
            'Host': f'{serverIP}:{port}',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Transfer-Encoding': 'identity',
            'Content-Type': 'text/html'
        }
        
        request = handle_post_request(filePath)
        if request == None:
            break
        print("no. chunks:", len(request))
        for i in range(len(request)):
            client.send(request[i])
            print('{address}, chunk: {no} sent'.format(address='127.0.0.1', no=i+1))
        print(client.recv(1024).decode())
        # # attaching host header
        # request = f"GET {filePath} HTTP/1.1\r\nAccept: */*\r\nCache-Control: no-cache\r\nHost: {serverIP}:{port}\r\nAccept-Encoding: gzip, deflate, br\r\nConnection: keep-alive\r\n"
        # client.send(request.encode())
        # response = client.recv(3072).decode()
        # print(response)
        # respondArray = response.split('\r\n', 1)
        # statusLine = respondArray[0]
        # header = respondArray[1].split('\r\n\r\n')[0]
        # # in case of GET a file is saved in the current directory if file is found in the server               
        # # if file requested is found in the server (check status line)
        # if (statusLine == 'HTTP/1.1 200 OK'): 
        #     fileType = getValueOfHeaderField(header, 'Content-Type')
        #     if (filePath[0] == '/'): filePath = '.' + filePath
        #     checkChuncked = True
        #     if (getValueOfHeaderField(header, 'Transfer-Encoding') == None): 
        #         checkChuncked = False
        #     # in case it is an image
        #     if (fileType == 'image/png' or fileType == 'image/jpg'):
        #         if (checkChuncked):
        #             with open(filePath, 'wb') as image:
        #                 response = b''
        #                 chunkNumber = 1
        #                 # loop on image size for accepting all image chunks
        #                 while (b'0\r\n\r\n' not in response):
        #                     response = client.recv(3007)
        #                     chunkContent = response.split(b'\r\n', 1)
        #                     chunkSize = int(chunkContent[0].decode(), 16)
        #                     body = chunkContent[1]
        #                     if (b'0\r\n\r\n' not in response):
        #                         body = body.rstrip(b'\r\n0\r\n\r\n')  
        #                     else:   
        #                         body = body.rstrip(b'\r\n')
                                
        #                     image.write(body)
        #                     print("chunk number: ", chunkNumber, "chunk size: ", chunkSize, "\n", body)
        #                     chunkNumber += 1
        #         else:
        #             with open(filePath, 'wb') as image:
        #                 body = respondArray[1].split('\r\n\r\n')[1].encode()
        #                 image.write(body)
        #     # in case it is a text file   
        #     elif (fileType == 'text/txt' or fileType == 'text/html'):    
        #         if (checkChuncked):
        #             with open(filePath, 'w') as file:
        #                 chunkNumber = 1
        #                 response = ''
        #                 while('0\r\n\r\n' not in response):
        #                     response = client.recv(3007).decode()
        #                     chunkContent = response.split('\r\n')
        #                     chunkSize = int(chunkContent[0], 16)
        #                     body = chunkContent[1]
        #                     file.write(body)
        #                     print("chunk Number: ", chunkNumber, "chunk size: ", chunkSize, "\n", body)
        #                     chunkNumber += 1
                            
        #         else:
        #             with open(filePath, 'w') as file:
        #                 body = respondArray[1].split('\r\n\r\n')[1]
        #                 file.write(body)

        client.sendall("CLOSE".encode())
        print(client.recv(1024).decode())
        client.close()
        break
    except(ConnectionAbortedError, ConnectionResetError):
        print("Server is closed!")
        client.close()
        break
    
    
    

