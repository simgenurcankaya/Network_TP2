import threading
import socket

SEGMENT_SIZE = 100

 # scp -i ../../.ssh/id_geni_ssh_rsa -P 28813  e2099554@pc3.lan.sdn.uky.edu:r3_s.txt r3_s.txt
# ssh -i .ssh/id_geni_ssh_rsa e2099554@pc2.instageni.colorado.edu -p 28813
#e2099554@pc2.instageni.colorado.edu:25414, 
# ssh -i .ssh/id_geni_ssh_rsa e2099554@pc2.instageni.colorado.edu -p 25414


## IP's for D node
ip_send_r1 = "10.10.4.1"
ip_get_r1 = "10.10.4.2"
ip_send_r2= "10.10.5.1"
ip_get_r2 = "10.10.5.2"
ip_send_r3 = "10.10.7.2"
ip_get_r3 = "10.10.7.1"

#Ports for D node
port_r1= 23426 
port_r2= 44004 
port_r3= 45678 

#Sockets used in D
sockR1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockR2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockR3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Function to receive 1000 messages from R3


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

 

def send(content, to):
    checksum = ip_checksum(content)
    send_sock.sendto(checksum + content, to)


if __name__ == "__main__":
    sockR3.bind((ip_get_r3,port_r3))

    expecting_seq = 0

    while True:
        message, address = sockR3.recvfrom(4096)

        checksum = message[:2]
        seq = message[2]
        content = message[3:]

        if ip_checksum(content) == checksum:
            sockR3.sendto("ACK"+seq,(ip_send_r3,port_r3))
            if seq == str(expecting_seq):
                print content[0::10]
                expecting_seq = 1 - expecting_seq
        else:
            negative_seq = str(1 - expecting_seq)
            sockR3.sendto("ACK"+negative_seq,(ip_send_r3,port_r3))

