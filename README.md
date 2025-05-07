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
