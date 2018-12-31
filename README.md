# Manipulative-DNS-Proxy
A DNS Proxy that uses UDP and TCP to route requests and responses through an existing DNS.

This program routes incoming DNS messages through an existing DNS resolver (Google's free DNS) and then provides the answers to the client. However, if the Domain name is not found by the resolver (a "No Such Name" response is received) then a fake message is generated that routes the user to a given IP (taken as a command line argument to the script).

#### The flow of the program


This was a class assigment.
