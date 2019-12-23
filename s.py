import threading
import socket
import time

#For the experiment we only needed S-R3-D implementation,
#so other ports are not implemented.
#S sends and receives only from R3
ip_send_r3 = "10.10.3.2"    
ip_get_r3 = "10.10.3.1"

port_r3= 35437 

MAX_SEGMENT = 4000

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


def readFile(filename, packet_size,offsping):
    with open(filename) as file:
        while True:
            packet = file.read(packet_size)
            if not packet:
                break
            yield packet


#Function to send a message
def sendR3(ip,port):
    print "Sending from S "
    i = 0

    with open("input.txt") as f:
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
        print i
        i += 1
        print "offset : ",offset
        print "segment size : ", len(segment)
        sockR3.sendto(segment , (ip, port))  #send message to r3
        print "\nFinished sending \n"
        try:
            data, server = sockR3.recvfrom(4096) #wait for ACK from r3
            print "Received : ", data
        except: 
            print "Error occured in R3-S"
   

if __name__ == "__main__":

    sendR3(ip_send_r3,port_r3)

    print("Done!") 