import threading
import socket
import time

#For the experiment we only needed S-R3-D implementation,
#so other ports are not implemented.
#S sends and receives only from R3
ip_send_r3 = "10.10.3.2"    
ip_get_r3 = "10.10.3.1"

port1_r3 = 35437 
port2_r3 = 35438
number_of_ack = 0


MAX_SEGMENT = 950

sock1_R3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2_R3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1_R3.settimeout(1)  # set timeout to the socket 
sock2_R3.settimeout(1)  # set timeout to the socket 

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


def sendR3port1(ip,port):
    print "Sending from S1 "
    i = 0

    with open("di.txt") as f:
        content = f.read()
    seq = 0
    print len(content)
    offset = 0
    segment = 0
    while offset < len(content)/2:
        if offset + MAX_SEGMENT > len(content)/2:
            segment = content[offset:len(content)/2]
        else:
            segment = content[offset:offset+MAX_SEGMENT]
        offset += MAX_SEGMENT
        print "offset : ",offset
        print "segment size : ", len(segment)

        ack_received = False
        while not ack_received:

            sock1_R3.settimeout(1)
            checksum = ip_checksum(segment)
            print "Size of checksum" , len(checksum)
            sock1_R3.sendto( checksum + str(seq) + segment , (ip, port))  #send message to r3
            print "Sending packet ", segment[0:10]
            print "Finished sending packet ", i
            
            i += 1
            try:
                print "wait for ackk"
                data, server = sock1_R3.recvfrom(1024) #wait for ACK from r3
            except: 
                print "Couldn't get the ACK"
                pass
            else:
                print "Received : ", data
                if data[3] == '0':
                    print "ACK Received"
                    seq = (seq+1) %2
                    ack_received = True
                elif data[3] == '1':
                    print "NAK Received"
                else:
                    print "Invalid return data"
    isEOFacked = False

    while not isEOFacked:                
        try:
            sock1_R3.sendto("EOF",(ip, port))
        except:
            "Eof ACKED HATASIII 1"
            pass

        try:
            print "wait for ackk1"
            data, server = sock1_R3.recvfrom(1024) #wait for ACK from r3
        except: 
            print "Couldn't get the ACK1"
            pass
        else:
            if data == "ACK0":
                print "EOF acklandi 1"
                isEOFacked =True
            else:
                print "EOF NAK1"


def sendR3port2(ip,port):
    print "Sending from S2 "
    i = 0

    with open("di.txt") as f:
        content = f.read()
    seq  =0
    print len(content)
    offset = len(content)/2
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

            sock2_R3.settimeout(1)
            checksum = ip_checksum(segment)
            print "Size of checksum" , len(checksum)
            sock2_R3.sendto( checksum+ str(seq)+ segment , (ip, port))  #send message to r3
            print "Sending packet ", segment[0:10]
            print "Finished sending packet ", i
            
            i += 1 
            try:
                print "wait for ackk"
                data, server = sock2_R3.recvfrom(1024) #wait for ACK from r3
            except: 
                print "Couldn't get the ACK"
                pass
            else:
                print "Received : ", data
                if data[3] == '0':
                    print "ACK Received"
                    seq =(seq+1)%2
                    ack_received = True
                elif data[3] == '1':
                    print "NAK Received"
                else:
                    print "Invalid return data"
            
    isEOFacked = False

    while not isEOFacked:                
        try:
            sock2_R3.sendto("EOF",(ip, port))
        except:
            "Eof ACKED HATASIII 2"
            pass

        try:
            print "wait for ackk2"
            data, server = sock2_R3.recvfrom(1024) #wait for ACK from r3
        except: 
            print "Couldn't get the ACK2"
            pass
        else:
            if data == "ACK0":
                print "EOF acklandi 2"
                isEOFacked =True
            else:
                print "EOF NAK1"

    


if __name__ == "__main__":
 
    x = threading.Thread(target=sendR3port1,args=(ip_send_r3,port1_r3))
    y = threading.Thread(target=sendR3port2,args=(ip_send_r3,port2_r3))
   
    x.start()
    y.start()


    print("Done!") 