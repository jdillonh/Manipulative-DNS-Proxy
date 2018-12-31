## Some code based on https://pymotw.com/2/socket/udp.html
import select
import socket
import sys



########## Debugging help - delete later
import os
# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

###########



TIMEOUT = None #for select



def handleUDP(openSock):
    #print "handling UDP"
    query, add = openSock.recvfrom(4096)

    # Create socket for upstream resolver (Google)
    upstreamSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    upstreamSock.connect((dnsResolver, 53))

    sent = upstreamSock.send(query)
    data = upstreamSock.recv(4096)
    
    #print 'ip address: ', ipAddress   
    ipAddHex = ipAddress.split('.')
    ipAddHex = '{:02X}{:02X}{:02X}{:02X}'.format(*map(int, ipAddHex))
    
    #print data[0]
    rcodeVal = int(bin(ord(data[3])), 2) & 15
    #print 'rcode: ', rcodeVal
    if rcodeVal == 3:
        data = list(data)
        zero = str(bytearray.fromhex('00'))
        one = str(bytearray.fromhex('01'))


        data[2] = str(bytearray.fromhex('84'))

        data[3] = zero #rcode


        data[6]  = zero 
        data[7]  = one 
        data[8]  = zero 
        data[9]  = zero
        data[10] = zero
        data[11] =  zero

        #End of header,
        #Now questions
        i = 12
        while 1:
            if data[i] == bytearray.fromhex('00'):
                i += 1
                break
            else:
                i += 1

        #Now i points at the beggining of Answers
        #Skip query type & class
        i += 3
        #now put in answer
        #get rid of rest
        data = data[0:i+1] #TODO +1?
     #   print data


        data = ''.join(data)
         
        #data += ''.join(queryName)
        data += bytearray.fromhex('c00c')
        
        data += zero #type A
        data += one
        
        data += zero #class
        data += one 

        data +=  bytearray.fromhex('0000012b') #time to live, TTL TODO is this right

        data += bytearray.fromhex('0004') #data length

        data += bytearray.fromhex(ipAddHex) #IP Address
        #data += bytearray.fromhex('12e10b63')       
 
        #print data


    openSock.sendto(data, add)
    #print "Packet Sent"
    #upstreamSock.close()
    return 0

def handleTCP(openSock): 
    #print "handling TCP"

    connSock, userAddTCP = openSock.accept()

    ## Receive query from client
    query =  connSock.recv(1024)
    ## Get size of query
    size = ord(query[0]) * 256 + ord(query[1])   + 2

    # print "size: ", size

    ## Receive entire query (if necessary)
    received = len(query)
    while received < size:
     #   print received
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
    size = ord(data[0]) * 256 + ord(data[1]) + 2 # add 2 for the length bytes?
    
    received = len(data)
    while received < size:
   #     print 'received: ', received
        newMessage = upstreamSock.recv(1024)
        received += len(newMessage)
        data += newMessage

    #print 'data: ', data
    #print 'ord(' ') = ', ord(' ')
    #print 'ord(data[0]): ', ord(data[0])
    #print 'ord(data[1]): ', ord(data[1])
    #print 'ord(data[4]): ', ord(data[4])
    #print 'ord(data[5]): ', bin(ord(data[5]))[2:]
    #print '6th byte: ', bin(ord(data[5]))
        # print 'accurately identified dns answer'
    ## Send the answer to client
    connSock.send( data )
    connSock.close()
    upstreamSock.close()
    return 0


ipAddress = sys.argv[len(sys.argv)-1]
dnsResolver = '8.8.8.8'
## Create UDP and TCP sockets
userSockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
userSockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

userSockUDP.bind(('',53))
userSockTCP.bind(('',53))
userSockTCP.listen(5)

rlist = [userSockUDP, userSockTCP]

while True:
    # print "top of the loop"
    read, _, exception = select.select(rlist, [], [], TIMEOUT)

    if len(read) >= 1 :
        for openSock in read:

            if openSock == userSockUDP:
                handleUDP(userSockUDP)
            if openSock == userSockTCP:
                handleTCP(userSockTCP)

    else:
        ## Hit an error, TODO this may not always be an error, what about wlist.
        raise Exception('bad socket or something')
