import socket
import time
import threading
import logging

#For the experiment we only needed S-R3-D implementation,
#so other ports are not implemented.

#R3 is between S and D , receives from S , sends to D
ip_send_s = "10.10.3.1"
ip_get_s = "10.10.3.2"

ip_send_d = "10.10.7.1"
ip_get_d = "10.10.7.2"

port_s = 35437
port_d = 45678

Message = "- Sent by R3- "

sockS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockD = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sockS.bind((ip_get_s,port_s)) #binding the ports

def getS():
    i = 0
    isEOF = False  #Check if the input ended to close the socket.
    while not isEOF:
        print "Now getting from S number " ,i
        try: 
            sockS.settimeout(1)  #set timeout to both sockets
            sockD.settimeout(1)
            datafromS, addressS = sockS.recvfrom(1024)  #waiting for data
            i += 1 
            if datafromS == "EOF":  #EOF reached, send it to the D, then terminate.
                isEOF = True
            print "Data received from S, now sending it to D"
            sockD.sendto(datafromS , (ip_send_d,port_d)) #sends the received data from S to D
        except:
            print "Error when sending the data to D"
            pass
        try:
            datafromD, addressD = sockD.recvfrom(1024) #Waits for ACK from D
            print "Data from D : ", datafromD
            print "Data received from D, now sending it back to S"
            sockS.sendto(datafromD, addressS) #Sends ACK to S
        except:
            print "Error when sending the ack to S"
            pass


if __name__ == "__main__":
    getS()

    print("Done!") 
