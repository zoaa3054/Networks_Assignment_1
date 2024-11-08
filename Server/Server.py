import threading
import socket
import asyncio
import time
# global variable for time out of the server in sec

SuccessStatusLine = 'HTTP/1.1 200 OK\r\n'
NotFoundStatusLine = 'HTTP/1.1 404 Not Found\r\n'


# function for getting the file size
def get_file_size(file):
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    return size

def parse_http_request(request):
    """Parses an HTTP request and returns a tuple containing the method, URL,
    version, headers, and body.

    Parameters:
        request (str): The HTTP request to parse.

    Returns:
        tuple: A tuple containing the method, URL, version, headers, and body.
    """
    # Split the request into lines
    lines = request.split('\r\n')

    # Extract the method, URL, and version from the first line
    print("head line: ",lines[0])
    method, url, version = lines[0].split(" ")

    # Initialize the headers and body
    headers = {}
    body = ''

    # Iterate over the lines, splitting each one into a key-value pair
    for line in lines[1:]:
        if line == '':
            break
        key, value = line.split(': ', 1)
        headers[key] = value

    # Set the body to the last line
    body = lines[-1]

    # Return the parsed request as a tuple
    return method, url, version, headers, body

def handle_get_text_file_request(url):
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

    try:
        with open(url, 'r') as file:
            file_size = get_file_size(file)
            # Read the entire file if its size is less than 512 bytes
            if file_size < 512:
                response_body = file.read()
    except FileNotFoundError:
        # Return a 404 Not Found response if the file is not found
        return [
            '{status}Content-Type: text/{file_extension}\r\n\r\n<h1> Page not found </h1>\r\n\r\n'
            .format(status=NotFoundStatusLine, file_extension=file_extension)
            .encode()
        ]

    # If the file size is small, send it as a single response
    if file_size < 200:
        return [
            '{status}Content-Type: text/{file_extension}\r\nContent-Length: {file_size}\r\n\r\n{response_body}'
            .format(
                status=SuccessStatusLine,
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
            '{status}Content-Type: text/{file_extension}\r\nTransfer-Encoding: chunked\r\n\r\n'
            .format(status=SuccessStatusLine, file_extension=file_extension, file_size=file_size)
            .encode()
        )

        # Read and send the file in chunks of 1024 bytes
        with open(url, 'r') as file:
            while file_size > 0:
                file_content = file.read(3000)
                size = str(hex(len(file_content))).replace("0x",'')
                response.append('{size}\r\n{content}\r\n'.format(size=size,content=file_content).encode())
                file_size -= 3000


        # Indicate the end of the chunked transfer
        response.append(b'0\r\n\r\n')
        return response

def handle_get_image_request(url):
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
        return [
            "{status}Content-Type: image/{extension}\r\n\r\n"
            .format(status=NotFoundStatusLine, extension=extension)
            .encode()
        ]

    # If the file size is small, send it as a single response
    if file_size < 2048:
        with open(url, 'rb') as file:
            response_body = file.read()
        return [
            "{status}Content-Type: image/{extension}\r\nContent-Length: {size}\r\n\r\n"
            .format(status=SuccessStatusLine, size=file_size, extension=extension)
            .encode()
            + response_body + '\r\n'.encode()
        ]

    # Use chunked transfer encoding for larger files
    response = []
    response.append(
        "{status}Content-Type: image/{extension}\r\nContent-Length: {size}\r\nTransfer-Encoding: chunked\r\n\r\n"
        .format(status=SuccessStatusLine, extension=extension, size=file_size)
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

def handle_get_request(method, url, version, headers):
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
            return handle_get_text_file_request('.' + url) 
        else:
            return handle_get_text_file_request(url)
    
    if extension == 'png' or extension == 'gif' or extension == 'jpg' or extension == 'jpeg' or extension == 'ico' or extension == 'icon':
        print("image")
        if list(url)[0] == '/':
            return handle_get_image_request('.' + url) 
        else:
                return handle_get_image_request(url)
            

    return ["{status}Content-Type: text/html\r\n\r\n<h1> Page not found </h1>"
            .format(status=NotFoundStatusLine).encode()]

def handle_post_request_not_chunked(url, headers, body):
    with open("."+ url, 'w') as file:
        if(headers['Content-Type'].split('/')[0] == 'text'):
            file.write(body.decode())
        else:
            file.write(body)
    
    return ["{status}Content-Type: text/html\r\n\r\n".format(status=SuccessStatusLine).encode()]

def handle_post_request_chunked(url, headers, channel):
    end_of_chunk = b'0\r\n\r\n'

    request = channel.recv(3072).decode()
    while request != end_of_chunk.decode():
        with open("."+ url, 'ab') as file:
            if(headers['Content-Type'].split('/')[0] == 'text'):
                file.write(request.decode().split('\r\n')[1])
            else:
                file.write(request.decode().split('\r\n')[1].encode())
        request = channel.recv(3072).decode()


# function of the work done by some connection on a separate thread
def startWork(server, channel, address):
    while True:
        # accepting the request and printing it
        request = channel.recv(3072).decode()

        parsedRequest = parse_http_request(request)
        print("method: ", parsedRequest[0])
        print("url: ", parsedRequest[1])
        print("version: ", parsedRequest[2])
        print("headers: ", parsedRequest[3].keys())
        print("body: ", parsedRequest[4])

        if (parsedRequest[0] == "CLOSE"):
            channel.send("CLOSED".encode())
            break

        if (parsedRequest[0] == "GET"):
            print("GET request")
            response = handle_get_request(parsedRequest[0], parsedRequest[1], parsedRequest[2], parsedRequest[3])
            print("no. chunks:", len(response))
            for i in range(len(response)):
                channel.send(response[i])
                print('{address}, chunk: {no} sent'.format(address=address, no=i+1))

        if (parsedRequest[0] == "POST"):
            if 'Transfer-Encoding' in parsedRequest[3].keys():
                if parsedRequest[3]['Transfer-Encoding'] == "chunked":
                    print("POST request chunked")
                    response = handle_post_request_chunked(parsedRequest[1], parsedRequest[3],parsedRequest[4])
                    channel.send(response)
                else:
                    print("POST request not chunked")
                    channel.send("{status}Content-Type: text/html\r\n\r\n".format(status=SuccessStatusLine).encode())
                    handle_post_request_not_chunked(parsedRequest[1], parsedRequest[3], channel)
            

        if parsedRequest[3]['Connection'] == "close":
            break


    channel.close()

     
# initializing the server socket for TCP handshaking
port = 8000
ip = '127.0.0.1'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((ip, port))

# start listening for the incoming
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
    