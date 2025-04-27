# DRTP: DATA2410 Reliable Transport Protocol
## DATA2410 Home Exam

## How to run
Run the server with `application.py` with:
```sh
 python3 application.py -s -i <server_ip_adresss> -p <port> -w <window_size> -d <discard_packet>
```
Where -s = server mode

Run the client with `application.py` with:
```sh
python3 application.py -c -f <file_name> -i <server_ip_adresss> -p <server_port> -w <window_size>
```
where -c = client mode

Possibly replace python3 with py if running on windows