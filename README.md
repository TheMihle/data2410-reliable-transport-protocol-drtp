# DRTP: DATA2410 Reliable Transport Protocol
## Home Exam
### Grade archived: A

## Overview
This application was developed as the home exam of the DATA2410 Networking and cloud computing course. 
The application can be run as a server and client and transfers a jpeg image reliably from the client to the server. 

The transfer is done via the designed DRTP protocol built on top of UDP. It implements connections with a three-way handshake.
It also uses the Go-Back-N strategy for reliability with a sliding window to increase the throughput.

It was developed for and tested in Mininet.

Some small changes have been made since delivery of the exam, check out the [at-delivery branch](/../at-delivery/) or 
earlier commits for the delivered version.

For more information about the implementation, result of tests and discussion around some aspects, written 
based on the delivered exam code, see the [documentation PDF](/documentation.pdf).

## How to run:
Run the server with `application.py` with:
```sh
 python3 application.py -s -i <server_ip_adresss> -p <server_port> -d <discard_packet_number>
```
where `-s` = server mode.


Run the client with `application.py` with:
```sh
python3 application.py -c -i <server_ip_adresss> -p <server_port> -f <file_name> -w <window_size>
```
where `-c` = client mode.

For more information, see  
```sh
python3 application.py --help
```
This code was tested on mininet.

## How to test in mininet
 - If you have a non-Linux OS: Install Ubuntu or other compatible distribution in Virtualbox or other VM hypervisor.
 - Install Mininet, xterm, openvswitch-switch.
 - Transfer the files to the VM, can be done with a shared folder or other methods.
 - Run a mininet topology file you want to test with.
 - Open the nodes you want to run the client and server on with xterm (In this case, the client was run on h1 and server on h2).
 - Use the commands above to run the server and client with the right IP and other arguments.
 - Study the results.