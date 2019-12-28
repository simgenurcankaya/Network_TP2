import threading
import socket
import time


#  IP's given
ip_send_r1 = "10.10.1.2"
ip_get_r1 = "10.10.1.1"
ip_send_r2= "10.10.2.1"
ip_get_r2 = "10.10.2.2"
ip_send_r3 = "10.10.3.2"    
ip_get_r3 = "10.10.3.1"

#Port's declared
port1_r1 = 35435 
port2_r1 = 35436 
port1_r2 = 53516 
port2_r2 = 53517
port1_r3 = 35437 
port2_r3 = 35438


number_of_ack = 0

#file segments to append
fileSegments = []
isEOF = False
# Global Variables for Multi-Homing

isOpenPort1 = True
isOpenPort2 = True

handshakePortR1 =57084
handshakePortR2 =57085

handshakeSockPort1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
handshakeSockPort2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
handshakeSockPort1.settimeout(11)
handshakeSockPort2.settimeout(11)

# Global Variables for Window
window = []
windowFillerIndex = 0

# Segment size
MAX_SEGMENT = 950


# Sockets
sock1_R3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2_R3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1_R3.settimeout(1)  # set timeout to the socket 
sock2_R3.settimeout(1)  # set timeout to the socket 

sock1_R1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2_R1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1_R2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2_R2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1_R1.settimeout(1)
sock1_R2.settimeout(1)
sock2_R1.settimeout(1)
sock2_R2.settimeout(1)

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

#send to port1 of r3
def sendR3port1(ip,port):
    print "Sending from S1 "
    i = 0
    #open file 
    with open("input1.txt") as f:
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

        # get the data by sliding the offset
        ack_received = False
        while not ack_received: #if not acked continue

            sock1_R3.settimeout(1)
            checksum = ip_checksum(segment)
            print "Size of checksum" , len(checksum)
            sock1_R3.sendto( checksum + str(seq) + segment , (ip, port))  #send message to r3
            print "Sending packet ", segment[0:10]
            print "Finished sending packet ", seq
            
            i += 1
            try:
                print "wait for ackk 1 "
                data, server = sock1_R3.recvfrom(1024) #wait for ACK from r3
            except: 
                print "Couldn't get the ACK 1"
                pass
            else:
                print "Received : ", data
                if data[3] == '0':
                    print "ACK Received1"
                    seq = (seq+1) %2
                    ack_received = True
                elif data[3] == '1':
                    print "NAK Received1"
                else:
                    print "Invalid return data1"
    isEOFacked = False

    while not isEOFacked:   # send ack to EOF to close the ports             
        try:
            sock1_R3.sendto("EOF",(ip, port))
        except:
            "Eof ACKED HATASIII 1"
            pass

        try:
            print "wait for eof ackk1"
            data, server = sock1_R3.recvfrom(1024) #wait for ACK from r3
        except: 
            print "Couldn't get the eof ACK1"
            pass
        else:
            if data == "ACK0":
                print "EOF acklandi 1"
                isEOFacked =True
            else:
                print "EOF NAK1"

#send to port2 of r3
def sendR3port2(ip,port):
    print "Sending from S2 "
    i = 0

    #open file 
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

# get the data by sliding the offset
        ack_received = False
        while not ack_received: #if not acked continue

            sock2_R3.settimeout(1)
            checksum = ip_checksum(segment)
            print "Size of checksum" , len(checksum)
            sock2_R3.sendto( checksum+ str(seq)+ segment , (ip, port))  #send message to r3
            print "Sending packet ", segment[0:10]
            print "Finished sending packet ", seq
            
            i += 1 
            try:
                print "wait for ackk2"
                data, server = sock2_R3.recvfrom(1024) #wait for ACK from r3
            except: 
                print "Couldn't get the ACK2"
                pass
            else:
                print "Received : ", data
                if data[3] == '0':
                    print "ACK Received2"
                    seq =(seq+1)%2
                    ack_received = True
                elif data[3] == '1':
                    print "NAK Received2"
                else:
                    print "Invalid return data2"
            
    isEOFacked = False

    while not isEOFacked:   # send ack to EOF to close the ports 
        try:
            sock2_R3.sendto("EOF",(ip, port))
        except:
            "Eof ACKED HATASIII 2"
            pass

        try:
            print "wait for eof ackk2"
            data, server = sock2_R3.recvfrom(1024) #wait for ACK from r3
        except: 
            print "Couldn't get the eof ACK2"
            pass
        else:
            if data == "ACK0":
                print "EOF acklandi 2"
                isEOFacked =True
            else:
                print "EOF NAK1"


# send port function for experiment 2 
#send to given socket with gicen ip and port
def sendPort(data,ip,port,sock):
    global window

    print "Sending from S "
    i = 0
    segment = data[4:]
    sock.settimeout(1)
    checksum = ip_checksum(segment)
    print "Size of checksum" , len(checksum)
    sock.sendto(checksum +  data[:4]  + segment , (ip, port))  #send message to r3
    print "Sending packet ", segment[0:10]

    try:
        print "wait for ackk",data[:4] 
        lol, server = sock.recvfrom(1024) #wait for ACK from r3
    except: 
        print "Couldn't get the ACK", data[:4]

        window.append(segment)
        return False
        pass

    print "Received : ", lol
    if data[3] == '0':
        print "ACK Received",data[:4]
        
        return True
    elif data[3] == '1':
        print "NAK Received" ,data[:4]
        window.append(segment)
        return False
    else:
        print "Invalid return data"
        window.append(segment)
        return False

def sendPort1(data,ip,port):
    global window

    print "Sending from S "
    i = 0
    segment = data[4:]
    checksum = ip_checksum(segment)
    print "Size of checksum" , len(checksum)
    sock1_R1.sendto(checksum +  data[:4]  + segment , (ip, port))  #send message to r3
    print "Sending packet ", segment[0:10]

    try:
        print "wait for ackk",data[:4] 
        dataFromR1, server = sock1_R1.recvfrom(1024) #wait for ACK from r3
    except: 
        print "Couldn't get the ACK", data[:4]

        window.append(segment)
        return False
        pass

    print "Received : ", dataFromR1
    if dataFromR1[3] == '0':
        print "ACK Received", data[:4]
        
        return True
    elif dataFromR1[3] == '1':
        print "NAK Received",data[:4]
        window.append(segment)
        return False
    else:
        print "Invalid return data"
        window.append(segment)
        return False


#divide the file to segments 
# add seq num starting from 1000 to the front
def divideTheFile():
    global fileSegments
    file = open("input1.txt","rb")
    content = file.read()
    offset = 0
    i = 1000
    while offset < len(content):
        if offset + MAX_SEGMENT > len(content):
            segment = content[offset:len(content)]
        else:
            segment = content[offset:offset+MAX_SEGMENT]
        offset += MAX_SEGMENT
        print "offset : ",offset
        print "segment size : ", len(segment)
        segment = str(i) + segment
        fileSegments.append(segment)
        i+= 1

    print "dividing finished, segment len = ", len(fileSegments)
    print "window i = " ,i 


#fills the window the be exactly len 4

def windowFiller():
    global windowFillerIndex
    global window
    global fileSegments
    global isEOF

    print "Filling the window"
    print "Arriving window" , window
    while len(window) <4:
        if windowFillerIndex >= len(fileSegments):
            isEOF = True
            break
        window.append(fileSegments[windowFillerIndex]) 
        windowFillerIndex+=1
    
    print "Window is full"
    #print window

#for checking the ports
def checkPorts():
    print "Checking the ports"
    global isOpenPort1
    global isOpenPort2

    isOpenPort1 = True
    isOpenPort2 = True
    # isOpenPort1 = threeWayHandshake(ip_send_r1,handshakePortR1,handshakeSockPort1)
    # isOpenPort2 = threeWayHandshake(ip_send_r2,handshakePortR2,handshakeSockPort2)

    print "isport1 open " ,isOpenPort1
    print "isport2 open " ,isOpenPort2

#the three way handshake protocol implemented
def threeWayHandshake(ip,port,sock):
    print "Sending sync"
    sock.sendto("SYN" , (ip, port))
    i = 0
    ret = False
    while i<5:
        try:
            print "wait for ack",i
            i+=1
            data, server  = sock.recv(1024)
        except: 
            print "couldnt get"
            pass
        else:
            print "got ", data
            ret = True
    return True

#Multi-homing sender to the 4 ports at the same time using 4 threads
def multihomingSender():
    global window
    global fileSegments
    global multiHomeRes
    global isEOF
    global isOpenPort1
    global isOpenPort2

    print "Multihoming started"
    sended = 0
    while not isEOF:
        i = 0
        #fill the window
        windowFiller()
        #if window is empty
        if len(window) == 0:
            print "Window empty" 
            isEOF = True
            window.append("EOF")
        #check for a time
        if(sended %20 == 0) or (not isOpenPort1 or not isOpenPort2):
            checkPorts()
        #sends if the port is open
        if isOpenPort1 == True: 
            print "Sending to R1"
            x = threading.Thread(target=sendPort1,args=(window[0], ip_send_r1,port1_r1))
            x.start()
            window = window[1:]
            y = threading.Thread(target=sendPort,args=(window[0], ip_send_r1,port2_r1,sock2_R1))
            y.start()
            window = window[1:]
        #sends if the port is open
        if isOpenPort2 == True:
            print "Sending to R2"
            x = threading.Thread(target=sendPort,args=(window[0], ip_send_r2,port1_r2,sock1_R2))
            x.start()
            window = window[1:]
            y = threading.Thread(target=sendPort,args=(window[0], ip_send_r2,port2_r2,sock1_R2))
            y.start()
            window = window[1:]
    


if __name__ == "__main__":

    input_ = raw_input("Which experiment? : ")

    if input_ == "1" :
    
        x = threading.Thread(target=sendR3port1,args=(ip_send_r3,port1_r3))
        y = threading.Thread(target=sendR3port2,args=(ip_send_r3,port2_r3))
    
        x.start()
        y.start()

    elif input_ == "2":
        divideTheFile()
        multihomingSender()

    else:
        print "Wrong experiment number. Choose either 1 or 2"

