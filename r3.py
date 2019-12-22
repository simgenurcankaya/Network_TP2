import socket
import time
import threading
import logging

## IP's for R3 node
ip_get_r2 = "10.10.6.2" 
ip_send_r2 = "10.10.6.1"

ip_send_s = "10.10.3.1"
ip_get_s = "10.10.3.2"

ip_send_d = "10.10.7.1"
ip_get_d = "10.10.7.2"

#Ports for R3 node
port_r2= 32001
port_s = 35437
port_d = 45678

Message = "Sent by R3 "

#Sockets used in R3
sockS = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockD = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sockS.bind((ip_get_s,port_s))

def receiveR3():
    expecting_seq = 0
    print "Listening..."
    while True:
        try:
            datafromS, addressS = sockS.recvfrom(4096)
            print "Received packet from sender:", datafromS[0::10]
        except error:
            print "Error occured in R3-S" #timeout
        sockD.sendto(datafromS, (ip_send_d,port_d))
        try:
            datafromD = sockD.recv(4096)
            print "Received packet from receiver:", datafromD[0::10]
        except error:
            print "Error occured in R3-D"
        print "Data received from D, now sending it back to S"
        sockS.sendto(pkt, (ip_send_s,port_s))    

if __name__ == "__main__":

    receiveR3()

    # t1 = threading.Thread(target=sendS, args=(ip_send_s,port_s)) 
    # t2 = threading.Thread(target=sendD, args=(ip_send_d,port_d)) 
    # t3 = threading.Thread(target=sendR2, args=(ip_send_r2,port_r2)) 
  
    # # starting thread 1 
    # t1.start() 
    # # starting thread 2 
    # t2.start() 
    #  # starting thread 3 
    # t3.start()
    # # wait until thread 1 is completely executed 
    # t1.join() 
    # # wait until thread 2 is completely executed 
    # t2.join() 
    # # wait until thread 3 is completely executed 
    # t3.join()

    # print t1.isAlive()
    # print t2.isAlive()
    # print t3.isAlive()

    # both threads completely executed 
    print("Done!") 

    # #After threads are DONE, close the files,
    # r3_d.close()
    # r3_s.close()
    # r3_r2.close()

 
