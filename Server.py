import threading
import socket
import asyncio

# global variable for time out of the server in sec
timeout = 5
# function for checking idlty
async def checkIdle(server, channel=None):
    # time allowed for idlty 
    await asyncio.sleep(timeout)
    # if it is only the parent thread (server) is running and the channel which is about to close
    # or in case at the beginning where no channels are yet created
    if (threading.active_count() == 2):
        if (channel is not None):
            channel.close()
        server.close()
        return True    
    return False

# function for checking the idlty at the beginning running on a separate thread
def beginningIdleThreade(server, status):
    asyncio.run(checkIdle(server=server))
    
# function of the work done by some connection on a separate thread
def startWork(server, channel, address):
    while (True):
        incomming = channel.recv(1024).decode()
        print(address , " >> ", incomming)
        if (incomming.upper() == "CLOSE"):
            channel.send("closed".encode())
            # checking if there are other channels running
            if (not asyncio.run(checkIdle(server=server, channel=channel))):
                channel.close()
            return
        outgoing = input("you >> ")
        channel.send(outgoing.encode())

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
    # create Idle checker thread at the beginning only
    if beginingSwitch: 
        threading.Thread(target=beginningIdleThreade, args=(server, 0)).start()
        beginingSwitch = False
    
    try:
        newChannel, address = server.accept()
    except(socket.error):
        print("Server closed due to time out (5sec)!")
        break

    print("new connection accepted: ", address)
    newChannelThread = threading.Thread(target= startWork, args= (server, newChannel, address))
    newChannelThread.start()
    
