import threading
import socket
import time

#For the experiment we only needed S-R3-D implementation,
#so other ports are not implemented.

# D is the Destination and only receives from and sends to R3.
ip_send_r3 = "10.10.7.2"
ip_get_r3 = "10.10.7.1"

port1_d = 45678
port2_d = 45679

datafromS1 = []
datafromS2 = []
Simge = ""
totalDatafromS = 0 

isEOF =  False

lock_thread1 = threading.Lock()
lock_thread2 = threading.Lock()

sock1_R3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1_R3.bind((ip_get_r3,port1_d))
sock2_R3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2_R3.bind((ip_get_r3,port2_d))


expected_seq1 = 0  #0,2,0,2...
expected_seq2 = 1  #1,3,1,3...
mutex1 = threading.Lock()
mutex2 = threading.Lock()
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



def receiveR3_1():
    global totalDatafromS
    global datafromS1
    expected_seq1 = 1000
    isEOF = False

    while not isEOF:
        print "Thread 1 receiving"
        data, addr = sock1_R3.recvfrom(1024) 
        checksum = data[:2]  #checksum
        seq = data[2:6] #seq number 
        content = data[6:] #packet received

        print "Received " + content[0:10] + "in Thread 1"
        print  "Thread 1 expected seq = " + str(expected_seq1) + " coming seq " + seq

        if content == "EOF":
            isEOF = True
            break

        if ip_checksum(content) == checksum: #dogru gelmis, kaydet
            sock1_R3.sendto("ACK"+seq, addr) 
            if str(expected_seq1) == seq: #bekledigimiz geldi
                expected_seq1 +=2
                datafromS1.append(content)
                totalDatafromS +=1
            else:       
                print "lol"
        else:
            sock1_R3.sendto("NAK"+str(expected_seq1), addr)      
    print "Finished getting port1 with len = " ,len(datafromS1)

    if mutex1.locked():
        mutex1.release()        
            
def receiveR3_2():
    global totalDatafromS
    global datafromS2
    expected_seq2 = 1001
    isEOF = False

    while not isEOF:
        print "Thread 2 receiving"
        data, addr = sock2_R3.recvfrom(1024) 
        checksum = data[:2]  #checksum
        seq = data[2:6] #seq number 
        content = data[6:] #packet received

        print "Received " + content[0:10] + "in Thread 2"
        print  "Thread 2 expected seq = " + str(expected_seq2) + " coming seq " + seq

        if content == "EOF":
            isEOF = True
            break

        if ip_checksum(content) == checksum: #dogru gelmis, kaydet 
            sock2_R3.sendto("ACK"+seq, addr) 
            if str(expected_seq2) == seq: #bekledigimiz geldi
                expected_seq2 +=2
                datafromS2.append(content)
                totalDatafromS +=1
            else:
                print "helo"       
                #sock2_R3.sendto("NAK"+str(expected_seq2), addr) 
        else:
            sock2_R3.sendto("NAK"+str(expected_seq2), addr)    
        
    print "Finished getting port2 with len = " ,len(datafromS2) 
    if mutex2.locked():
        mutex2.release()

def connector():
    global datafromS1
    global datafromS2
    global Simge

    while(mutex1.locked() or mutex2.locked()):
        time.sleep(4)

    i = 0
    size = min(len(datafromS1) ,len(datafromS2))
    while i < size:
        Simge += datafromS1[i]
        Simge += datafromS2[i]
        i+=1
    if len(datafromS1)!=size:
        Simge+= datafromS1[i]

    g = open("simge.txt","w")
    g.write(Simge)
    

    print "Connector ended"        
            
    



             ## file arrived correctly
#             sock1_R3.sendto("ACK0", addr) #Sends ACK       
#             if str(expected_seq1) == seq:  #expected seq arrived, save it 
#             #    print "Message received rom D to R3: ", content
#                 print "Data received port1 with seq " ,expected_seq1
#                 print "total data from s thread 1 : ", totalDatafromS 
#                 print content[0:10]
#                 if(datafromS[expected_seq1] != ""):
#                     print "Data already exist in thread 1 seq = " + seq + " Waiting for write func" 
#                     lock_thread1.acquire()
#                     while lock_thread1.locked():
#                         i +=1
#                     print "Lock released"
#                     print "Data from s after lock release in thread 1 : ",  totalDatafromS
#                 datafromS[expected_seq1] = content
#                 expected_seq1 = (expected_seq1+2) %4 # alternates bw 0,2,0,2,0....
#                 totalDatafromS +=1
#                 if totalDatafromS ==4:
#                     saveFromS()
#             else:
#                 print "----- FILE WITH WRONG SEQ NUMBER HAS ARRIVED IN THREAD 1 -----" , expected_seq1
                
#         else: ##wrong file
#             print "Sending NAK in thread 1 to seq : " + seq
#             sock1_R3.sendto("NAK0", addr)
    

# def saveFromS():

#     global totalDatafromS
#     global datafromS
#     global lock_thread1
#     global lock_thread2
#     global mutex
#     global Simge
#     mutex.acquire()

#     print "Inside save function total data s : " , totalDatafromS
#     if(totalDatafromS != 0):
#         print "Writing data"
#         f.write(datafromS[0])
#         f.write(datafromS[1])
#         f.write(datafromS[2])
#         f.write(datafromS[3])
#         Simge += datafromS[0]
#         Simge += datafromS[1]
#         Simge += datafromS[2]
#         Simge += datafromS[3]

#         datafromS = ["","","",""]

#         totalDatafromS = 0

#         print "Size of Simge : " , len(Simge)

#         print "Finished writing"
#         time.sleep(1)
#         if lock_thread1.locked() == True:
#             print "Releasing lock1"
#             lock_thread1.release()
#         if lock_thread2.locked() == True:
#             print "Releasing lock2"
#             lock_thread2.release() 

#     if lock_thread1.locked() == True:
#         print "Releasing lock1"
#         lock_thread1.release()
#     if lock_thread2.locked() == True:
#         print "Releasing lock2"
#         lock_thread2.release() 
#     mutex.release()

# #Function to get a message
# def get1_R3(ip,port):
#     global expected_seq1
#     global datafromS
#     global totalDatafromS
#     global mutex
#     global lock_thread1
#     global isEOF
#     global thread2
#     global Simge

#     sock1_R3.settimeout(50)

#     while not isEOF:
#         while mutex.locked():
#             i = 0
#             #print "mutex bekliyor th1"
#         data, addr = sock1_R3.recvfrom(1024) 
#         checksum = data[:2]  #checksum
#         seq = data[2] #seq number 
#         content = data[3:] #packet received
#         i  =0 
#         if content == "EOF" or len(content) <80 : #EOF is reached, terminate. 
#             print "EOF mu geldi1"
#             isEOF = True
#             sock1_R3.sendto("ACK0", addr) 
#             saveFromS()

#             g = open("simge1.txt","w")
#             g.write(Simge)
#             lock_thread2.release()
#             sock1_R3.close()
#             sock2_R3.close()
#             break

#         if ip_checksum(content) == checksum:  ## file arrived correctly
#             sock1_R3.sendto("ACK0", addr) #Sends ACK       
#             if str(expected_seq1) == seq:  #expected seq arrived, save it 
#             #    print "Message received rom D to R3: ", content
#                 print "Data received port1 with seq " ,expected_seq1
#                 print "total data from s thread 1 : ", totalDatafromS 
#                 print content[0:10]
#                 if(datafromS[expected_seq1] != ""):
#                     print "Data already exist in thread 1 seq = " + seq + " Waiting for write func" 
#                     lock_thread1.acquire()
#                     while lock_thread1.locked():
#                         i +=1
#                     print "Lock released"
#                     print "Data from s after lock release in thread 1 : ",  totalDatafromS
#                 datafromS[expected_seq1] = content
#                 expected_seq1 = (expected_seq1+2) %4 # alternates bw 0,2,0,2,0....
#                 totalDatafromS +=1
#                 if totalDatafromS ==4:
#                     saveFromS()
#             else:
#                 print "----- FILE WITH WRONG SEQ NUMBER HAS ARRIVED IN THREAD 1 -----" , expected_seq1
                
#         else: ##wrong file
#             print "Sending NAK in thread 1 to seq : " + seq
#             sock1_R3.sendto("NAK0", addr)

#     print "get1_R3 terminates"

# def get2_R3(ip,port):
#     global expected_seq2
#     global datafromS
#     global totalDatafromS
#     global mutex 
#     global lock_thread2
#     global isEOF
#     global thread1
#     global Simge

#     i = 0
#     sock2_R3.settimeout(50)
#     while not isEOF:
#         while mutex.locked():
#             t = 1#            print "mutex bekliyor th2"
        
#         data, addr = sock2_R3.recvfrom(1024) 
#         checksum = data[:2]  #checksum
#         seq = data[2] #seq number 
#         content = data[3:] #packet received
#         i = 0
#         if content == "EOF" or len(content) <80: #EOF is reached, terminate. 
#             print "EOF mu geldi2 "
#             isEOF = True
#             sock2_R3.sendto("ACK1", addr)
#             saveFromS()
#             g = open("simge2.txt","w")
#             g.write(Simge)

#             lock_thread2.release()
#             sock1_R3.close()
#             sock2_R3.close()
#             break

#         if ip_checksum(content) == checksum:  ## file arrived correctly
#             sock2_R3.sendto("ACK1", addr) #Sends ACK       
#             if str(expected_seq2) == seq:  #expected seq arrived, save it 
#             #    print "Message received rom D to R3: ", content
#                 print "Data received port2 with seq " ,expected_seq2
#                 print "total data from thread 2 " , totalDatafromS
#                 print content[0:10]
#                 if(datafromS[expected_seq2] != ""):
#                     print "Data already exist in thread 2 seq = " + seq + " Waiting for write func"
#                     lock_thread2.acquire()
#                     while lock_thread2.locked():
#                         i+=1
#                     print "Lock released"
#                     print "Data from s after lock release in thread 2 : ",  totalDatafromS
#                 datafromS[expected_seq2] = content
#                 expected_seq2 = (expected_seq2+2) %4# alternates bw 1,3,1,3....
#                 totalDatafromS +=1
#                 if totalDatafromS ==4:
#                     saveFromS()
#             else:
#                 print "----- FILE WITH WRONG SEQ NUMBER HAS ARRIVED -THREAD 2----" , expected_seq2
                
#         else: ##wrong file
#             print "Sending NAK in thread 2 to seq : " + seq
#             sock2_R3.sendto("NAK1", addr)

#     print "get2_R3 terminates"

if __name__ == "__main__":

    thread1 = threading.Thread(target=receiveR3_1, args=()).start()
    thread2 = threading.Thread(target=receiveR3_2, args=()).start()
    thread3 = threading.Thread(target=connector, args=()).start()


    print("Done!") 