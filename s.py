import threading
import socket
import time

#For the experiment we only needed S-R3-D implementation,
#so other ports are not implemented.
#S sends and receives only from R3
ip_send_r3 = "10.10.3.2"    
ip_get_r3 = "10.10.3.1"

port_r3= 35437 

MAX_SEGMENT = 100

sockR3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Code taken from http://codewiki.wikispaces.com/ip_checksum.py.

def ip_checksum(data):  # Form the standard IP-suite checksum
    pos = len(data)
    if (pos & 1):  # If odd...
        pos -= 1
        sum = ord(data[pos])  # Prime the sum with the odd end byte
    else:
        sum = 0

    #Main code: loop to calculate the checksum
    while pos > 0:
        pos -= 2
        sum += (ord(data[pos + 1]) << 8) + ord(data[pos])

    sum = (sum >> 16) + (sum & 0xffff)
    sum += (sum >> 16)

    result = (~ sum) & 0xffff  # Keep lower 16 bits
    result = result >> 8 | ((result & 0xff) << 8)  # Swap bytes
    return chr(result / 256) + chr(result % 256)


# TODO implement sequence number 

def sendR3(ip,port):
    print "Sending from S "
    i = 0

    with open("di.txt") as f:
        content = f.read()
    
    print len(content)
    offset = 0
    segment = 0
    while offset < len(content):
        if offset + MAX_SEGMENT > len(content):
            segment = content[offset:]
        else:
            segment = content[offset:offset+MAX_SEGMENT]
        offset += MAX_SEGMENT
        print "offset : ",offset
        print "segment size : ", len(segment)

        ack_received = False
        while not ack_received:

            sockR3.settimeout(1)
            checksum = ip_checksum(segment)
            print "Size of checksum" , len(checksum)
            sockR3.sendto( checksum+ segment , (ip, port))  #send message to r3
            print "Sending packet ", segment
            print "Finished sending packet ", i
            
            i += 1
            try:
                print "wait for ackk"
                data, server = sockR3.recvfrom(1024) #wait for ACK from r3
            except: 
                print "Couldn't get the ACK"
                pass
            else:
                print "Received : ", data
                if data[3] == '0':
                    print "ACK Received"
                    ack_received = True
                elif data[3] == '1':
                    print "NAK Received"
                else:
                    print "Invalid return data"
    sockR3.sendto("EOF",(ip, port))


if __name__ == "__main__":

    sendR3(ip_send_r3,port_r3)

    print("Done!") 