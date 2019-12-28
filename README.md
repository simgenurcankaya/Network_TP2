# Ceng 435 Term Project 1
```python
#Simge Nur Çankaya 2099554
#Muhammed Süha Demirel 2098911

```
In the second part of the term project we created our own reliable data protocol over UDP, using technologies like checksum, re-transmission, ACK/NACK mechanism, sequence number, buffering, etc that provides the transmission of a large file between two hosts in a reliable and pipelining multi-homed approach.

## Installation
Send each script to its respected node via scp.

r1.py -> r1

r2.py, conf_1, conf_2,conf_3 -> r2

r3.py, conf_1, conf_2,conf_3 -> r3

s.py, conf_1, conf_2,conf_3 -> s

d.py  -> d


## Experiment 1

In order to do experiment 1:
send text file to the s as input1.txt
in s node: 
```bash
python s.py
```
in d node: 
```bash
python d.py
```
in r3 node: 
```bash
python r3.py
```
run files in the following order. d, r3, s

the file output1.txt is created on node d.

## Experiment 2
In order to do experiment 2:
send text file to the s as input2.txt

in s node: 
```bash
python s.py
```
in d node: 
```bash
python d.py
```
in r1 node: 
```bash
python r1.py
```
in r2 node: 
```bash
python r2.py
```
run files in the following order. d, r1 ,r2 , s

the file output2.txt is created on node d.

