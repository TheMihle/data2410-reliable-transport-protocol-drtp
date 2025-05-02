import sys
from socket import *
from utils import *
from datetime import datetime
from time import sleep

# Constants
RECEIVER_WINDOW = 15
# TODO: Check if how you should do this constant


def establish_connection(server_socket, server_address, port, window):
    message, (client_address, client_port) = server_socket.recvfrom(1000)
    seq_num, ack_num, flags, window = read_packet(message)
    server_socket.settimeout(0.4)

    if Flag.SYN in Flag(flags):
        print("SYN packet is received")
        sleep(0.2)
        server_socket.sendto(create_packet(0, ack_num, Flag.SYN | Flag.ACK, window), (client_address, client_port))
        print("SYN-ACK packet is sent")

    else:
        print("Received packet missing SYN flag")

    message, (client_address, client_port) = server_socket.recvfrom(1000)
    seq_num, ack_num, flags, window = read_packet(message)

    if Flag.ACK in Flag(flags):
        print("ACK packet is received")
        print("Connection Established\n")
        sleep(0.3)
    else:
        print("Received packet missing ACK flag")

    return seq_num, ack_num, window

def server(server_address, port, discard_packet):
    """
    Runs the server part of the application
    :param server_address:
    :param port: Port that the server will listen to
    :param discard_packet: Sequence number of the packet that should be discarded once
    """
    server_socket = socket(AF_INET, SOCK_DGRAM)
    try:
        server_socket.bind(('', port))
    except OSError as e:
        print(f"Binding failed with port {port}, Error: {e}")
        sys.exit()

    seq_num, ack_num, window = establish_connection(server_socket, server_address, port, RECEIVER_WINDOW)

    # Checks if the connection is ready to close. Responds with FIN ACK if so, then closes. Otherwise, treats the data
    while True:
        message, (client_address, client_port) = server_socket.recvfrom(1000)
        seq_num, ack_num, flags, window = read_packet(message)

        if flags == 0:
            print(f"{datetime.now().strftime("%H:%M:%S.%f")} -- packet {seq_num} is received")
            sleep(0.3)
            server_socket.sendto(create_packet(seq_num, ack_num, Flag.ACK, 0), (client_address, client_port))
            print(f"{datetime.now().strftime("%H:%M:%S.%f")} -- ACK for packet with seq = {seq_num} sent")

        elif Flag.FIN in Flag(flags):
            print("\nFIN packet is received")
            server_socket.sendto(create_packet(0, ack_num, Flag.FIN | Flag.ACK, 0),
                                 (client_address, client_port))
            print("FIN-ACK packet is sent")
            server_socket.close()

            print("\nCalculated throughput that haven't been calculated yet")
            print("Connection Closed")
            break

    print("\nExiting server")
    sys.exit()
