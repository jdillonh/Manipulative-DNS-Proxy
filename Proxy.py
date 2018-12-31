import select
import socket
import sys



def handleUDP(openSock):
    """
    Handle DNS query and response over a UDP connection.
    
    Arguments: openSock -- an open UDP socket that is ready to be recieved on.
    """
    query, add = openSock.recvfrom(4096)

    # Create socket for upstream resolver 
    upstreamSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    upstreamSock.connect((dnsResolver, 53))

    sent = upstreamSock.send(query)
    data = upstreamSock.recv(4096)
      
    ipAddHex = ipAddress.split('.')
    ipAddHex = '{:02X}{:02X}{:02X}{:02X}'.format(*map(int, ipAddHex))
  
    rcodeVal = int(bin(ord(data[3])), 2) & 15
    if rcodeVal == 3:
        # rcodeVal == 3 when there is a No Such Name Error
        # Build fake DNS Header
        data = list(data)
        zero = str(bytearray.fromhex('00'))
        one = str(bytearray.fromhex('01'))

        data[2]  = str(bytearray.fromhex('84'))
        data[3]  = zero 
        data[6]  = zero 
        data[7]  = one 
        data[8]  = zero 
        data[9]  = zero
        data[10] = zero
        data[11] = zero

        #Add Questions
        i = 12
        while 1:
            if data[i] == bytearray.fromhex('00'):
                i += 1
                break
            else:
                i += 1

        #Now i points at the beggining of Answers
        i += 3
        data = data[0:i+1]
        data = ''.join(data)

        data += bytearray.fromhex('c00c')        
        data += zero 
        data += one
        
        data += zero #Type field, let it be A (as opposed to MX, NS, etc.)
        data += one 

        data += bytearray.fromhex('0000012b') # TTL field
        data += bytearray.fromhex('0004')     # data length
        data += bytearray.fromhex(ipAddHex)   # IP Address
       
    openSock.sendto(data, add)
    return 0


def handleTCP(openSock): 
    """
    Handles a DNS query and response over a TCP connection.
    
    Arguments: openSock -- an open TCP socket that is ready to be recived on.
    """
    connSock, userAddTCP = openSock.accept()

    ## Receive query from client
    query =  connSock.recv(1024)
    ## Get size of query
    size = ord(query[0]) * 256 + ord(query[1])   + 2


    ## Receive entire query (if necessary)
    received = len(query)
    while received < size:
        newMessage = connSock.recv(1024)
        received += len(newMessage)
        query += newMessage
    
    ## Create socket for upstream resolver (Google)
    upstreamSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    upstreamSock.connect((dnsResolver, 53))

    ## Send the query to the upstream resolver
    upstreamSock.send(query) 
    
    ## Receive the answer from the upstream resolver
    data = upstreamSock.recv(4096)
    size = ord(data[0]) * 256 + ord(data[1]) + 2 # add 2 for the length bytes
    
    received = len(data)
    while received < size:
        newMessage = upstreamSock.recv(1024)
        received += len(newMessage)
        data += newMessage

    ## Send the answer to client
    connSock.send( data )
    connSock.close()
    upstreamSock.close()
    return 0



# Constants and Arguments
ipAddress = sys.argv[len(sys.argv)-1]
dnsResolver = '8.8.8.8'
TIMEOUT = None #None -> infinity


# Create UDP and TCP sockets
userSockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
userSockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

userSockUDP.bind(('',53))
userSockTCP.bind(('',53))
userSockTCP.listen(5)

rlist = [userSockUDP, userSockTCP]

while True:
    read, _, exception = select.select(rlist, [], [], TIMEOUT)

    if len(read) >= 1 :
        for openSock in read:
            if openSock == userSockUDP:
                handleUDP(userSockUDP)
            if openSock == userSockTCP:
                handleTCP(userSockTCP)

    else:
        raise Exception('bad socket')
