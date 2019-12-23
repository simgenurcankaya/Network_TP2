import threading
import socket

#For the experiment we only needed S-R3-D implementation,
#so other ports are not implemented.

# D is the Destination and only receives from and sends to R3.
ip_send_r3 = "10.10.7.2"
ip_get_r3 = "10.10.7.1"

port_r3= 45678 

sockR3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockR3.bind((ip_get_r3,port_r3))
f = open("output.txt", 'a')
#Function to get a message
def getR3(ip,port):
    data, addr = sockR3.recvfrom(4096) #waiting for message
    f.write(data)
    print "Message received rom D to R3: ", data[0:10]
    sockR3.sendto("ACK", addr) #Sends ACK


if __name__ == "__main__":
    while 1:
        getR3(ip_get_r3,port_r3)
    print("Done!") 