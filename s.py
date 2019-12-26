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

window = [0,0]  #if acks received turns to  [1,1]

MAX_SEGMENT = 100

sockR3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockR3.settimeout(1)  # set timeout to the socket 

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
def packetSender(i,ip,port,segment,seq):
    global window
    global number_of_ack
    # wait for ACK before sending another packet
    while window[i] == 0:
        checksum = ip_checksum(segment)  # calculate checksum
        sockR3.sendto(checksum+ str(seq)+  segment , (ip, port))  #send message to r3
        print "sending data ",i
        print segment[0:10]
        # print "Sending packet ", segment
        print "Finished sending packet ",i
        try:
            print "wait for ackk",i
            data, server = sockR3.recvfrom(1024) #wait for ACK from r3
        except: 
            print "Couldn't get the ACK",i
            pass
        else:
            print "Received : ", data
            if data[3] == '0':
                print "ACK Received",i
                window[i] = 1
                number_of_ack +=1
            elif data[3] == '1':
                print "NAK Received",i
            else:
                print "Invalid return data" ,i 


def sendR3(ip):
    global window
    global number_of_ack
    print "Sending from S "
    
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
            else:
                segment1 = content[offset:]
                segment2 = "0"
        else:
            segment1 = content[offset:offset+MAX_SEGMENT]  # there is plenty of data
            segment2 = content[offset+MAX_SEGMENT:offset+MAX_SEGMENT+MAX_SEGMENT]
        offset += MAX_SEGMENT + MAX_SEGMENT  #increase the offset
        print "offset : ",offset
        print "segment1 size : ", len(segment1)
        print "segment2 size : ", len(segment2)

        window = [0,0]
        number_of_ack = 0
        thread1 = threading.Thread(target=packetSender, args=(0,ip,port1_r3,segment1,seq))
        thread2 = threading.Thread(target=packetSender, args=(1,ip,port2_r3,segment2,seq+1))

        seq  = (seq+2) %4
        print "Starting the threads"
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        print "Threads ended"
        

        
    thread1 = threading.Thread(target=packetSender, args=(0,ip,port1_r3,"EOF",seq)).start()
    thread2 = threading.Thread(target=packetSender, args=(1,ip,port2_r3,"EOF",seq+1)).start()


if __name__ == "__main__":

    sendR3(ip_send_r3)

    print("Done!") 