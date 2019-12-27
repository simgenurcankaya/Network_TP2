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

port1_s = 35437 
port2_s = 35438

port1_d = 45678
port2_d = 45679

Message = "- Sent by R3- "

sockS1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockS2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockD1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockD2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sockS1.bind((ip_get_s,port1_s)) #binding the ports
sockS2.bind((ip_get_s,port2_s)) #binding the ports

def getS1():
    i = 0
    isEOF = False  #Check if the input ended to close the socket.
    while not isEOF or TimeoutError:
        print "Now getting from S number " ,i
        try: 
            sockS1.settimeout(1)  #set timeout to both sockets
            sockD1.settimeout(1)
            datafromS, addressS = sockS1.recvfrom(1024)  #waiting for data
            i += 1 
            if datafromS == "EOF":  #EOF reached, send it to the D, then terminate.
                isEOF = True
            print "Data received from S, now sending it to D"
            sockD1.sendto(datafromS , (ip_send_d,port1_d)) #sends the received data from S to D
        except:
            print "Error when sending the data to D"
            pass
        try:
            datafromD, addressD = sockD1.recvfrom(1024) #Waits for ACK from D
            print "Data from D : ", datafromD
            print "Data received from D, now sending it back to S"
            sockS2.sendto(datafromD, addressS) #Sends ACK to S
        except:
            print "Error when sending the ack to S"
            pass


def getS2( ):
    i = 0
    isEOF = False  #Check if the input ended to close the socket.
    while not isEOF or TimeoutError:
        print "Now getting from S number " ,i
        try: 
            sockS2.settimeout(1)  #set timeout to both sockets
            sockD2.settimeout(1)
            datafromS, addressS = sockS2.recvfrom(1024)  #waiting for data
            i += 1 
            if datafromS == "EOF":  #EOF reached, send it to the D, then terminate.
                isEOF = True
            print "Data received from S, now sending it to D"
            sockD2.sendto(datafromS , (ip_send_d,port2_d)) #sends the received data from S to D
        except:
            print "Error when sending the data to D"
            pass
        try:
            datafromD, addressD = sockD2.recvfrom(1024) #Waits for ACK from D
            print "Data from D : ", datafromD
            print "Data received from D, now sending it back to S"
            sockS2.sendto(datafromD, addressS) #Sends ACK to S
        except:
            print "Error when sending the ack to S"
            pass

if __name__ == "__main__":

    x = threading.Thread(target=getS1, args=())
    y = threading.Thread(target=getS2, args=())

    x.start()
    y.start()
    print("Done!") 
