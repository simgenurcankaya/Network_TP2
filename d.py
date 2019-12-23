import threading
import socket

#For the experiment we only needed S-R3-D implementation,
#so other ports are not implemented.

# D is the Destination and only receives from and sends to R3.
ip_send_r3 = "10.10.7.2"
ip_get_r3 = "10.10.7.1"

port_r3= 45678 

sockR3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockR3.bind((ip_get_r3,port_r3))
f = open("output.txt", 'a')

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
def getR3(ip,port):

    expecting_seq = 0  #expected sequence number, initial value = 0 , alternates bw 0,1,0,1..
    i = 0
    sockR3.settimeout(100)
    isEOF =False
    while not isEOF:
        
        data, addr = sockR3.recvfrom(1024) 
        checksum = data[:2]  #checksum
        seq = data[2] #seq number 
        content = data[3:] #packet received

        if data == "EOF": #EOF is reached, terminate. 
            isEOF = True
            break

        if ip_checksum(content) == checksum:  ## file arrived correctly
            sockR3.sendto("ACK0", addr) #Sends ACK       
            if str(expecting_seq) == seq:  #expected seq arrived, save it 
                print "Message received rom D to R3: ", content
                print "Number is ",i
                i +=1
                f.write("i is "+ str(i)+ "\n")
                f.write(content)
                expecting_seq = 1-expecting_seq # alternates bw 0,1,0,1,0....
            else:
                print "----- FILE WITH WRONG SEQ NUMBER HAS ARRIVED -----"
                
        else: ##wrong file
            sockR3.sendto("ACK1", addr)

if __name__ == "__main__":
    getR3(ip_get_r3,port_r3)
    
    print("Done!") 