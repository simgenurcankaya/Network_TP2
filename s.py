import threading
import socket

## IP's for S node
ip_send_r1 = "10.10.1.2"
ip_get_r1 = "10.10.1.1"
ip_send_r2= "10.10.2.1"
ip_get_r2 = "10.10.2.2"
ip_send_r3 = "10.10.3.2"
ip_get_r3 = "10.10.3.1"

#Ports for S node
port_r1= 35435 
port_r2= 35436 
port_r3= 35437 

#Sockets used in S
sockR1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockR2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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

        
def readFile(filename, packet_size=800):
    with open(filename) as file:
        while True:
            packet = file.read(packet_size)
            if not packet:
                break
            yield packet



def sendR3():
    offset = 0
    seq = 0
    i =0
    print "Sending ... \n"
    while i<7:
        i+=1
        print "i now : ",i
        rows_generator = readFile("input.txt",900)
        txt = next(rows_generator, None)

#        txt = readFile("input.txt",900)
 
        packet = txt[0:]
        ack_received = False
        while not ack_received:
            print "Sending to R3 \n"
            sockR3.sendto(ip_checksum(packet) + str(seq) + packet, (ip_send_r3,port_r3))
            try:
                message, address = sockR3.recvfrom(4096)
            except:
                print "Timeout"
            
            print message[0::10]
            checksum = message[:2]
            ack_seq = message[5]
            if ip_checksum(message[2:]) == checksum and ack_seq == str(seq):
                print "Ack received! \n"
                ack_received = True

        seq = 1 - seqf

if __name__ == "__main__":
    sendR3()
  
    # t1 = threading.Thread(target=getR1, args=(ip_get_r1,po rt_r1)) 
    # t2 = threading.Thread(target=getR2, args=(ip_get_r2,port_r2)) 
    # t3 = threading.Thread(target=getR3, args=(ip_get_r3,port_r3))
    # # starting thread 1 
    # t1.start() 
    # # starting thread 2 
    # t2.start() 
    # # starting thread 3
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

