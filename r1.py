import socket
import time
import threading
import logging

#For the experiment we only needed S-R1-D implementation,
#so other ports are not implemented.

#R1 is between S and D , receives from S , sends to D
ip_send_s = "10.10.1.2"
ip_get_s = "10.10.1.1"

ip_send_d = "10.10.4.1"
ip_get_d = "10.10.4.2"

port1_s = 35435 
port2_s = 35436

portHS_s = 57084

port1_d = 23426
port2_d = 23427

Message = "- Sent by R1- "

sockS1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockS2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockD1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockD2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sockHS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sockS1.bind((ip_get_s,port1_s)) #binding the ports
sockS2.bind((ip_get_s,port2_s)) #binding the ports
sockHS.bind((ip_get_s,portHS_s)) #binding the ports

def getS1():
    i = 0
    isEOF = False  #Check if the input ended to close the socket.
    while not isEOF or TimeoutError:
        print "Thread 1 Now getting from S number " ,i
        try: 
            sockS1.settimeout(1)  #set timeout to both sockets
            sockD1.settimeout(1)
            datafromS1, addressS1 = sockS1.recvfrom(1024)  #waiting for data
            i += 1 
            if datafromS1 == "EOF":  #EOF reached, send it to the D, then terminate.
                isEOF = True
            print "Thread 1 Data received from S, now sending it to D"
            sockD1.sendto(datafromS1 , (ip_send_d,port1_d)) #sends the received data from S to D
        except:
            print "Thread 1 Error when sending the data to D"
            pass
        try:
            datafromD, addressD = sockD1.recvfrom(1024) #Waits for ACK from D
            print "Thread 1 Data from D : ", datafromD
            print "Thread 1 Data received from D, now sending it back to S"
            sockS1.sendto(datafromD1, (ip_send_s,port1_s)) #Sends ACK to S
        except:
            print "Thread 1 Error when sending the ack to S"
            pass


def getS2( ):
    i = 0
    isEOF = False  #Check if the input ended to close the socket.
    while not isEOF or TimeoutError:
        print "Thread 2 Now getting from S number " ,i
        try: 
            sockS2.settimeout(1)  #set timeout to both sockets
            sockD2.settimeout(1)
            datafromS2, addressS2 = sockS2.recvfrom(1024)  #waiting for data
            i += 1 
            if datafromS2 == "EOF":  #EOF reached, send it to the D, then terminate.
                isEOF = True
            print "Thread 2 Data received from S, now sending it to D"
            sockD2.sendto(datafromS2 , (ip_send_d,port2_d)) #sends the received data from S to D
        except:
            print "Thread 2 Error when sending the data to D"
            pass
        try:
            datafromD, addressD = sockD2.recvfrom(1024) #Waits for ACK from D
            print "Thread 2 Data from D : ", datafromD
            print "Thread 2 Data received from D, now sending it back to S"
            sockS2.sendto(datafromD, addressS2) #Sends ACK to S
        except:
            print "Thread 2 Error when sending the ack to S"
            pass

def getHS( ):
    i = 0
    isEOF = False  #Check if the input ended to close the socket.
    while not isEOF or TimeoutError:
        print "Thread 3 Now getting from S number " ,i
        try: 
            sockHS.settimeout(1)  #set timeout to sockets
            datafromHS, addressHS = sockHS.recvfrom(1024)  #waiting for data
            i += 1 
            if datafromS2 == "EOF":  #EOF reached, send it to the D, then terminate.
                isEOF = True
            print "Thread 3 Data received from S, now sending it to S"
            sockHS.sendto(datafromHS , (ip_send_s,portHS_s)) #sends the received data to S
        except:
            print "Thread 3 Error when sending the data to S"
            pass

if __name__ == "__main__":

    x = threading.Thread(target=getS1, args=())
    y = threading.Thread(target=getS2, args=())
    z = threading.Thread(target=getHS, args=())

    x.start()
    y.start()
    z.start()

    print("Done!") 
