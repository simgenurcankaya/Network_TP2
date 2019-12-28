import threading
import socket
import time

#For the experiment we only needed S-R3-D implementation,
#so other ports are not implemented.

# D is the Destination and only receives from and sends to R3.
ip_send_r3 = "10.10.7.2"
ip_get_r3 = "10.10.7.1"
ip_send_r1 = "10.10.4.1"
ip_get_r1 = "10.10.4.2"
ip_send_r2= "10.10.5.1"
ip_get_r2 = "10.10.5.2"

port1_d = 45678
port2_d = 45679
portR1_1 = 23426
portR1_2 = 23427
portR2_1 = 44004
portR2_2 = 44005

mutex_val = 0

isMultihomingEOF =False
receivedDataFromMultihoming = [""] * 7000

sock1_R3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1_R3.bind((ip_get_r3,port1_d))
sock2_R3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2_R3.bind((ip_get_r3,port2_d))

sock1_R2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1_R2.bind((ip_get_r2,portR2_1))
sock2_R2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2_R2.bind((ip_get_r2,portR2_2))

sock1_R1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1_R1.bind((ip_get_r1,portR1_1))
sock2_R1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2_R1.bind((ip_get_r1,portR1_2))

data1 = ""
data2 = ""

expected_seq1 = 0  #0,2,0,2...
expected_seq2 = 1  #1,3,1,3...

f = open("output1.txt", 'a')

def writeR3():
    global mutex_val
    global data1
    global data2

    while(mutex_val !=2):
        i = 0
    print "Data1 len: ", len(data1)

    print "Data2 len: ", len(data2)

    time.sleep(2)
    suh = open("suh.txt","a")
    suh.write(data1)
    suh.write(data2)
    print "Writing finished!"
    

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
 
#Function to get a message
def get1_R3(ip,port):
    
    global data1
    global mutex_val
    expecting_seq = 0
    i = 0
    sock1_R3.settimeout(10)
    isEOF =False
    
    while not isEOF:
        try:
            data, addr = sock1_R3.recvfrom(1024) 
        except:
            print "Sock 1 exception"
            pass
        
        checksum = data[:2]
        received_seq = data[2]
        content = data[3:]

        print "Message received rom D to R3 thread 1: ", content
        print "Number is ",i

        if data == "EOF":
            isEOF = True
            break

        if ip_checksum(content) == checksum:  ## correct file arrived
            sock1_R3.sendto("ACK0", addr) #Sends ACK
            print "checksum are equal"
            if str(expecting_seq) == received_seq:
                f = open("simg1.txt","a")
                f.write(content)
                data1 += content
                i +=1
                expecting_seq = (expecting_seq+1) %2
                #sock1_R3.sendto("ACK0", addr) #Sends ACK     
            else:
                print "Wrong seq number hasarrived thread1"  
        else: ##wrong file
            sock1_R3.sendto("ACK1", addr)
    mutex_val+=1
    try:
        sock1_R3.sendto("ACK0", addr)
    except :
        pass
    print "thread 1 finished"


def get2_R3(ip,port):
    
    global mutex_val
    global data2
    expecting_seq = 0
    i = 0
    sock2_R3.settimeout(10)
    isEOF =False
    while not isEOF:
        try:
            data, addr = sock2_R3.recvfrom(1024) 
        except:
            print "Port 2 exception"
            pass

        checksum = data[:2]
        received_seq = data[2]
        content = data[3:]

        if data == "EOF":
            isEOF = True
            break

        if ip_checksum(content) == checksum:  ## correct file arrived
            f = open("simg2.txt","a")
            sock2_R3.sendto("ACK0", addr) #Sends ACK    
            if str(expecting_seq) == received_seq:
                f.write(content)
                data2 += content
                print "Message received rom D to R3 thread 2: ", content
                print "Number is ",i
                expecting_seq = (expecting_seq+1) %2
                i +=1
            else:
                print "Wrong seq number hasarrived thread2"  
        else: ##wrong file
            sock2_R3.sendto("ACK1", addr)

    mutex_val+=1
    try:
        sock1_R3.sendto("ACK0", addr)
    except :
        pass
    print "thread2 finished"
    

def getS(ip,port,sock):
    global receivedDataFromMultihoming
    global isMultihomingEOF
    sock.settimeout(10)
    while not isMultihomingEOF:
        try:
            data, addr = sock.recvfrom(1024) 
        except:
            print "Port exception"
            pass
        
        if data == "EOF":
            isMultihomingEOF = True
            break
        
        checksum = data[:2]
        seq = data[2:6]
        content = data[6:]
       
        if ip_checksum(content) == checksum:  ## correct file arrived
            f = open("out1.txt","a")
            sock2_R3.sendto("ACK0", addr) #Sends ACK    
            if str(expecting_seq) == received_seq:
                f.write(content)
                index = int(seq)
                receivedDataFromMultihoming[index] = content
        else: ##wrong file
            sock2_R3.sendto("ACK1", addr)

def writeOut2():
    global isMultihomingEOF
    global receivedDataFromMultihoming
    while(!isMultihomingEOF)
        i = 0
    
    simgos = open("output2.txt","a")
    for i in receivedDataFromMultihoming:
        if i != "":
            a.write(i[5:] )

            
    simgos.close()

if __name__ == "__main__":

    # thread1 = threading.Thread(target=get1_R3, args=(ip_get_r3,port1_d)).start()
    # thread2 = threading.Thread(target=get2_R3, args=(ip_get_r3,port2_d)).start()
    # thread3 = threading.Thread(target=writeR3, args=()).start()

    thread4 = threading.Thread(target=getS, args=(ip_get_r1,portR1_1)).start()
    thread5 = threading.Thread(target=getS, args=(ip_get_r1,portR1_2)).start()
    thread6 = threading.Thread(target=getS, args=(ip_get_r2,portR2_1)).start()
    thread7 = threading.Thread(target=getS, args=(ip_get_r2,portR2_2)).start()

    print("Done!") 