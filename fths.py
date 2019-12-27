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

mutex1 = threading.Lock()

mutex2 = threading.Lock()

data1 = []
data2 = []

ack1 = []
ack2 = []

MAX_SEGMENT = 2

sock1_R3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2_R3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock1_R3.bind((ip_get_r3,port1_r3))
sock2_R3.bind((ip_get_r3,port2_r3))

sock1_R3.settimeout(1)  # set timeout to the socket 
sock2_R3.settimeout(1)  # set timeout to the socket 

isEOF = False

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


def receive1FromR3():
    
    global data1
    global ack1
    correctlySendedR3_by1 = 0
    dataFromR3 = ""
    while len(ack1)>0:
        
        print "Thread 1 receiving"
        try:
            
            dataFromR3, server = sock1_R3.recvfrom(1024)
            print "Data received from port1 : ", dataFromR3
        except:
            print "exception in receive1"
        finally:
        
            if dataFromR3[0:3] == "ACK":
                seq = int(dataFromR3[3:])
                index = (seq-1000) / 2
                print "Removing seq: " , ack1[index]
                ack1 = ack1[0:index] + ack1[index+1:]
                print "New seq to send : " ,ack1[0]
                correctlySendedR3_by1 +=1
            else: #NAK
                print "Nak received in thread 1"


def receive2FromR3():
    global data2
    global ack2
    correctlySendedR3_by2 = 0
    dataFromR3 = ""
    while len(ack2)>0:
        print "Thread 2 receiving"
        try:
            dataFromR3, server = sock2_R3.recvfrom(1024)
            print "Data received from port2 : ", dataFromR3
        except:
            print "exception in receive2"
        finally:
            if dataFromR3[0:3] == "ACK":
                seq = int(dataFromR3[3:])
                index = (seq-1001) / 2
                print "Removing seq: " , ack2[index]
                ack2 = ack2[0:index] + ack2[index+1:]
                print "New seq to send : ", ack2[0]
                correctlySendedR3_by2 +=1
            else: #NAK
                print "Nak received in thread 2"


def send1toR3():
    global data1
    global ack1

    while len(ack1)>0:
        print "Size of ack1 : ", len(ack1)
        print "Thread 1 Sending seq :", ack1[0]
        index = ack1[0] /2
        context = data1[index]
        seq = ack1[0]+1000

        sock1_R3.sendto(ip_checksum(context)+ str(seq)+  context , (ip_send_r3, port1_r3)) 


def send2toR3():
    global data2
    global ack2

    while len(ack2)>0:
        mutex2.acquire()
        print "Size of ack2 : ", len(ack2)
        print "Thread 2 Sending seq :", ack2[0]
        index = (ack2[0] -1) /2
        context = data2[index]
        seq = ack2[0]+1000

        sock2_R3.sendto(ip_checksum(context)+ str(seq)+  context , (ip_send_r3, port2_r3)) 



def packetCreator():
    global data1
    global data2
    global ack1
    global ack2
    
    with open("di.txt") as f:  #read input file 
        content = f.read()
    
    print len(content)
    offset = 0  # where to start taking the data sending
    segment1 = 0 # the data that will be send
    segment2 = 0
    seq = 0 # sequence number
    while offset < len(content):
        if offset + MAX_SEGMENT + MAX_SEGMENT> len(content):  # if there is not enough data left to full a mac segment
            if offset + MAX_SEGMENT < len(content):  #first segment full secons segment not
                segment1 = content[offset:offset+MAX_SEGMENT]
                segment2 = content[offset+MAX_SEGMENT:]
                ack1.append(seq)
                ack2.append(seq+1)
            else:
                segment1 = content[offset:]
                segment2 = ""
                ack1.append(seq)
        else:
            segment1 = content[offset:offset+MAX_SEGMENT]  # there is plenty of data
            segment2 = content[offset+MAX_SEGMENT:offset+MAX_SEGMENT+MAX_SEGMENT]
            ack1.append(seq)
            ack2.append(seq+1)
        offset += MAX_SEGMENT + MAX_SEGMENT  #increase the offset
        

        data1.append(segment1)
        if (segment2 !=""):
            data2.append(segment2)
        seq +=2
    data1.append("EOF")
    data2.append("EOF")

    print "Len of Data1 :" , len(data1)
    print "Len of Data2 :" , len(data2)

    print "Ack1 : " ,ack1[0:10]
    print "Ack2 : " ,ack2[0:10]

    print "Package 1 ", data1
    print "Package 2 ", data2


# # TODO implement sequence number 
# def packetSender(i,ip,port,segment,seq):
#     global window
#     global number_of_ack
#     # wait for ACK before sending another packet
#     while window[i] == 0:
#         checksum = ip_checksum(segment)  # calculate checksum
#         if i == 0:
#             sock1_R3.sendto(checksum+ str(seq)+  segment , (ip, port))  #send message to r3
#         else:
#             sock2_R3.sendto(checksum+ str(seq)+  segment , (ip, port))  #send message to r3
#         print "sending data "  + str(i) +" with seq number " + str(seq)
#         print segment[0:10]
#         # print "Sending packet ", segment
#         print "Finished sending packet ",i
#         try:
#             print "wait for ackk",i
#             if i == 0:
#                 data, server = sock1_R3.recvfrom(1024) #wait for ACK from r3
#             else:
#                 data, server = sock2_R3.recvfrom(1024) #wait for ACK from r3
#         except: 
#             print "Couldn't get the ACK",i
#             pass
#         else:
#             print "Received : ", data
            
#             if data == "ACK0":
#                 window[0] =1
#             elif data == "NAK0":
#                 window[0] = 0
#             elif data == "ACK1":
#                 window[1] = 1
#             elif data == "NAK1":
#                 window[1] = 0
#             else:
#                 print "BIG ERROR TIME"

# def sendR3(ip):
#     global window
#     global number_of_ack
#     global isEOF

#     print "Sending from S "
    
#     with open("di.txt") as f:  #read input file 
#         content = f.read()
    
#     print len(content)
#     offset = 0  # where to start taking the data sending
#     segment1 = 0 # the data that will be send
#     segment2 = 0
#     seq = 0 # sequence number
#     while offset < len(content):
#         if offset + MAX_SEGMENT + MAX_SEGMENT> len(content):  # if there is not enough data left to full a mac segment
#             if offset + MAX_SEGMENT < len(content):  #first segment full secons segment not
#                 segment1 = content[offset:offset+MAX_SEGMENT]
#                 segment2 = content[offset+MAX_SEGMENT:]
#             else:
#                 segment1 = content[offset:]
#                 isEOF = True
#                 segment2 = "EOF"
#         else:
#             segment1 = content[offset:offset+MAX_SEGMENT]  # there is plenty of data
#             segment2 = content[offset+MAX_SEGMENT:offset+MAX_SEGMENT+MAX_SEGMENT]
#         offset += MAX_SEGMENT + MAX_SEGMENT  #increase the offset
#         print "offset : ",offset
#         print "segment1 size : ", len(segment1)
#         print "segment2 size : ", len(segment2)

#         window = [0,0]
#         number_of_ack = 0
#         thread1 = threading.Thread(target=packetSender, args=(0,ip,port1_r3,segment1,seq))
#         thread2 = threading.Thread(target=packetSender, args=(1,ip,port2_r3,segment2,seq+1))

#         seq  = (seq+2) %4
#         print "Starting the threads"
#         thread1.start()
#         thread2.start()
#         thread1.join()
#         thread2.join()
#         print "Threads ended"
#     if isEOF == False:
#         thread1 = threading.Thread(target=packetSender, args=(0,ip,port1_r3,segment1,seq))
        


if __name__ == "__main__":
    packetCreator()

    threading.Thread(target=send1toR3, args=()).start()
    threading.Thread(target=receive1FromR3, args=()).start()
    threading.Thread(target=send2toR3, args=()).start()
    threading.Thread(target=receive2FromR3, args=()).start()
    

    print("Done!") 