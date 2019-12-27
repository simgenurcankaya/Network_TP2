import threading

#example script to test thread abilities

total_ack_number = 0

sender = 1;

receiver = 3;
ack_array = [0,0,0,0]

data = [5,6,14,2]
def send(i):
    global ack_array
    global total_ack_number
    global data
    
    data[i] += 12
    print "ending send"
    ack_array[i] = 1

def receive():
    global receiver 
    global sender
    global total_ack_number
    print "started receive()",receiver
    while receiver < 15:
        receiver += 1
        print "receiver nmber ", receiver
        print "sender nmber ", sender
        print "total_ack_number ",total_ack_number
    print "end receiver()"

def main():
    x = threading.Thread(target=send, args=())
    y = threading.Thread(target=receive, args=())

    x.start()
    y.start()

    "started threads"


main()