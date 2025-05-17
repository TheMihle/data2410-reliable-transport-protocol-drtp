# DRTP: DATA2410 Reliable Transport Protocol
## DATA2410 Home Exam

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
 - Open the nodes you want to run the client and server on with xterm (In this case, client was run on h1 and server on h2).
 - Use the commands above to run the server and client with the right IP and other arguments.
 - Study the results.