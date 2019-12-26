import threading
import socket

#For the experiment we only needed S-R3-D implementation,
#so other ports are not implemented.

# D is the Destination and only receives from and sends to R3.
ip_send_r3 = "10.10.7.2"
ip_get_r3 = "10.10.7.1"

port1_d = 45678
port2_d = 45679

datafromS = ["0","0","0","0"]
totalDatafromS = 0 

sock1_R3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1_R3.bind((ip_get_r3,port1_d))
sock2_R3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2_R3.bind((ip_get_r3,port2_d))


expected_seq1 = 0  #0,2,0,2...
expected_seq2 = 1  #1,3,1,3...

f = open("output1.txt", 'a')

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
 
def saveFromS():
    global datafromS
    global totalDatafromS

    f.write(datafromS[0])
    f.write(datafromS[1])
    f.write(datafromS[2])
    f.write(datafromS[3])

    datafromS = ["0","0","0","0"]

    totalDatafromS = 0 


#Function to get a message
def get1_R3(ip,port):
    global expected_seq1 #expected sequence number, initial value = 0 
    global datafromS
    global totalDatafromS
    sock1_R3.settimeout(100)
    isEOF =False
    while not isEOF:
        data, addr = sock1_R3.recvfrom(1024) 
        checksum = data[:2]  #checksum
        seq = data[2] #seq number 
        content = data[3:] #packet received
        
 

        if data == "EOF": #EOF is reached, terminate. 
            isEOF = True
            break

        if ip_checksum(content) == checksum:  ## file arrived correctly
            sock1_R3.sendto("ACK0", addr) #Sends ACK       
            if str(expected_seq1) == seq:  #expected seq arrived, save it 
            #    print "Message received rom D to R3: ", content
                print "Data received port1 with seq " ,expected_seq1
                print content[0:10]
                datafromS[expected_seq1] = content
                totalDatafromS +=1
                if totalDatafromS ==4:
                    saveFromS()
                expected_seq1 = (expected_seq1+2) %4 # alternates bw 0,1,0,1,0....
            else:
                print "----- FILE WITH WRONG SEQ NUMBER HAS ARRIVED IN THREAD 1 -----"
                
        else: ##wrong file
            sock1_R3.sendto("ACK1", addr)

def get2_R3(ip,port):
    global datafromS
    global totalDatafromS
    global expected_seq2 #expected sequence number, initial value = 0 , alternates bw 0,1,0,1..
    i = 0
    sock2_R3.settimeout(100)
    isEOF =False
    while not isEOF:
        
        data, addr = sock2_R3.recvfrom(1024) 
        checksum = data[:2]  #checksum
        seq = data[2] #seq number 
        content = data[3:] #packet received

        if data == "EOF": #EOF is reached, terminate. 
            isEOF = True
            break

        if ip_checksum(content) == checksum:  ## file arrived correctly
            sock2_R3.sendto("ACK0", addr) #Sends ACK       
            if str(expected_seq2) == seq:  #expected seq arrived, save it 
            #    print "Message received rom D to R3: ", content
                print "Data received port2 with seq " ,expected_seq2
                print content[0:10]
                datafromS[expected_seq2] = content
                totalDatafromS +=1
                if totalDatafromS ==4:
                    saveFromS()
                expected_seq2 = (expected_seq2+2) %4# alternates bw 0,1,0,1,0....
            else:
                print "----- FILE WITH WRONG SEQ NUMBER HAS ARRIVED -----"
                
        else: ##wrong file
            sock2_R3.sendto("ACK1", addr)

if __name__ == "__main__":

    thread1 = threading.Thread(target=get1_R3, args=(ip_get_r3,port1_d)).start()
    thread2 = threading.Thread(target=get2_R3, args=(ip_get_r3,port2_d)).start()

    print("Done!") 