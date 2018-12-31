# Manipulative-DNS-Proxy
A DNS Proxy that uses UDP and TCP to route requests and responses through an existing DNS.

This program routes incoming DNS messages through an existing DNS resolver (Google's free DNS) and then provides the answers to the client. However, if the Domain name is not found by the resolver (a "No Such Name" response is received) then a fake message is generated that routes the user to a given IP (taken as a command line argument to the script).

### The flow of the program
Select waits on the UDP and TCP sockets for an incoming request. Once one is found it is sent to the cooresponding function: handleUDP is for requests over UDP and handleTCP is for requests over TCP. 

Most requests are handled through UDP. All requests initally come in over UDP, but if the response is too large the DNS resolver will indicate that in the response, asking the user to resubmit the request with TCP. The user will resubmit the request and handleTCP will be called.


If the response comes in with a "No Such Name" response (DNS rcode == 3), then a phony DNS packet is created that redirects the user to the IP Address provided as the first argument to the script.

![dns-packet-header.jpg]
