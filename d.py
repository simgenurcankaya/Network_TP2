import threading
import socket
import time

#  IP's given
ip_send_r3 = "10.10.7.2"
ip_get_r3 = "10.10.7.1"
ip_send_r1 = "10.10.4.1"
ip_get_r1 = "10.10.4.2"
ip_send_r2= "10.10.5.1"
ip_get_r2 = "10.10.5.2"

#Port's declared
port1_d = 45678
port2_d = 45679
portR1_1 = 23426
portR1_2 = 23427
portR2_1 = 44004
portR2_2 = 44005

# mutex for file writing
mutex_val = 0
mutex = threading.Lock()

# global variables for multihoming
isMultihomingEOF =False
receivedDataFromMultihoming = [""] * 7000

# Sockets
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

#data to hold to given values
data1 = ""
data2 = ""

expected_seq1 = 0  #0,2,0,2...
expected_seq2 = 1  #1,3,1,3...


#f = open("output1.txt", 'w')
file1 = open("port1.txt","a")
file2 = open("port2.txt","a")

#to hold the time values

timenow = time.time()


#for writing to a file after receiving full data
def writeR3():
    global mutex_val
    global data1
    global data2
    global time

    while(mutex_val !=2):
        i = 0
    print "Data1 len: ", len(data1)

    print "Data2 len: ", len(data2)

    time.sleep(2)

    # for writing to output
    suh = open("output1.txt","a")
    suh.write(data1)
    suh.write(data2)
    
    #for writing the time differences to a file for easy access
    exp = open("exp.txt","a")
    x = time.time()
    exp.write("Start time : " + str(timenow)+"\n")
    exp.write("End time : " + str(x)+"\n")
    exp.write("Difference =  "+ str(timenow-x ))

    print "Writing finished!" , x


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
 
#Function to get data from port1 of R3
def get1_R3(ip,port):
    
    global data1
    global mutex_val
    expecting_seq = 0
    i = 0
    sock1_R3.settimeout(10)
    isEOF =False
    
    while not isEOF:
        try:
            data, addr = sock1_R3.recvfrom(1024)  #Receive data
        except:
            print "Sock 1 exception" 
            pass
        
        # fragment data
        checksum = data[:2]
        received_seq = data[2]
        content = data[3:]

        print "Message received rom D to R3 thread 1: ", content
        print "Number is ",i

        if data == "EOF":
            isEOF = True
            break
        print "In thread 1 EXpected seq =  " + str(expecting_seq) + " seq now  = " + received_seq

        if ip_checksum(content) == checksum:  ## correct data arrived
            sock1_R3.sendto("ACK0", addr) #Sends ACK
            print "checksum are equal"
            if str(expecting_seq) == received_seq:
                f = open("simg1.txt","a")
                f.write(content)
                data1 += content
                i +=1
                expecting_seq = (expecting_seq+1) %2 # expecting seq alters 0,1,0,1...
                #sock1_R3.sendto("ACK0", addr) #Sends ACK     
            else:
                print "Wrong seq number hasarrived thread1"  
        else: ##wrong file
            sock1_R3.sendto("ACK1", addr)

    #EOF received
    mutex_val+=1
    try:
        sock1_R3.sendto("ACK0", addr)
    except :
        pass
    print "thread 1 finished"

#Function to get data from port2 of R3
def get2_R3(ip,port):
    
    global mutex_val
    global data2
    expecting_seq = 0
    i = 0
    sock2_R3.settimeout(10)
    isEOF =False
    while not isEOF:
        try:
            data, addr = sock2_R3.recvfrom(1024) #Receive data
        except:
            print "Port 2 exception"
            pass

        # fragment data
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
                expecting_seq = (expecting_seq+1) %2  # expecting seq alters 0,1,0,1...
                i +=1
            else:
                print "Wrong seq number hasarrived thread2"  
        else: ##wrong file
            sock2_R3.sendto("ACK1", addr)

    #EOF received
    mutex_val+=1
    try:
        sock1_R3.sendto("ACK0", addr)
    except :
        pass
    print "thread2 finished"

 ## getS function for receiving from R1 and R2   
def getS(ip,port,sock):
    global receivedDataFromMultihoming
    global isMultihomingEOF
    sock.settimeout(100)
    while not isMultihomingEOF:
        data = ""
        try:
            data, addr = sock.recvfrom(1024) # receive data
        except:
            print "Port exception"
            pass
        
        if data == "EOF":
            isMultihomingEOF = True
            break
        
        checksum = data[:2]
        seq = data[2:6]
        content = data[6:]
        print "Data received = " , content[0:10] 
        print "seq " + seq
       
        if ip_checksum(content) == checksum:  ## correct file arrived
            f = open("out1.txt","a")
            sock2_R3.sendto("ACK0", addr) #Sends ACK    
            print "Sending ACK"
            f.write(content)
            index = int(seq)
            receivedDataFromMultihoming[index] = content #put data to list
        else: ##wrong file
            print "Sending NAK"
            sock2_R3.sendto("ACK1", addr)

#write the data received to the disk

def writeOut2():
    global isMultihomingEOF
    global receivedDataFromMultihoming
    while not isMultihomingEOF : #wait for EOF
        i = 0
    
    simgos = open("output2.txt","a")
    for i in receivedDataFromMultihoming:
        if i != "":
            a.write(i[5:] ) #write data without taking the seq #

            
    simgos.close()


if __name__ == "__main__":

    input_ = raw_input("Which experiment? : ")

    if(input_ =="1"):
        thread1 = threading.Thread(target=get1_R3, args=(ip_get_r3,port1_d)).start()
        thread2 = threading.Thread(target=get2_R3, args=(ip_get_r3,port2_d)).start()
        thread3 = threading.Thread(target=writeR3, args=()).start()
    
    if input_ =="2":

        thread4 = threading.Thread(target=getS, args=(ip_get_r1,portR1_1,sock1_R1)).start()
        thread5 = threading.Thread(target=getS, args=(ip_get_r1,portR1_2,sock1_R2)).start()
        thread6 = threading.Thread(target=getS, args=(ip_get_r2,portR2_1,sock2_R1)).start()
        thread7 = threading.Thread(target=getS, args=(ip_get_r2,portR2_2,sock2_R2)).start()
