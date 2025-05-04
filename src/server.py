import sys
from socket import *
from utils import *
from time import sleep

# Constants
RECEIVER_WINDOW = 15
# TODO: HIGHER TIMEOUT THAN 0.4 TO MAKE IT NOT TIME OUT WITH PACKET LOST
TIMEOUT = 0.5
# TODO: Check if how you should do this constant, bad practice to not have input in to function??


def establish_connection(server_socket, window):
    message, (client_address, client_port) = server_socket.recvfrom(1000)
    _seq_num, _ack_num, flags, _window, _data = parse_packet(message)
    server_socket.settimeout(TIMEOUT)

    if Flag.SYN in Flag(flags):
        print("SYN packet is received")
        sleep(0.2)
        server_socket.sendto(create_packet(0, 0, Flag.SYN | Flag.ACK, window), (client_address, client_port))
        print("SYN-ACK packet is sent")

    else:
        print("Received packet missing SYN flag")

    message, (client_address, client_port) = server_socket.recvfrom(1000)
    _seq_num, _ack_num, flags, _window, _data = parse_packet(message)

    if Flag.ACK in Flag(flags):
        print("ACK packet is received")
        print("Connection Established\n")
    else:
        print("Received packet missing ACK flag")


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

    # TODO: Should it be ready to wait for a new one after one closes?
    while True:
        establish_connection(server_socket, RECEIVER_WINDOW)

        # Checks if the connection is ready to close. Responds with FIN ACK if so, then closes. Otherwise, treats the data
        while True:
            next_seq_num = 1
            message, (client_address, client_port) = server_socket.recvfrom(1000)
            seq_num, ack_num, flags, _window, data = parse_packet(message)

            if flags == 0:
                # Ignores the packet once if the sequence number matches the one that should be discarded
                if seq_num == discard_packet:
                    discard_packet = -1
                    continue

                if seq_num != next_seq_num:
                    print(f"{time_now_log()} packet {seq_num} is received")
                sleep(0.05)
                server_socket.sendto(create_packet(seq_num, ack_num, Flag.ACK, 0), (client_address, client_port))
                print(f"{time_now_log()} ACK for packet with seq = {seq_num} sent")

            elif Flag.FIN in Flag(flags):
                print("\nFIN packet is received")
                sleep(0.2)
                server_socket.sendto(create_packet(0, 0, Flag.FIN | Flag.ACK, 0),
                                     (client_address, client_port))
                print("FIN-ACK packet is sent")

                # Sets timeout so it can listen for a new connection without error
                server_socket.settimeout(None)
                print("\nCalculated throughput that haven't been calculated yet")
                print("Connection Closed\n")
                break

    # TODO: Should socket be closed every time a connection is finished?
    server_socket.close()
    print("\nExiting server")
    sys.exit()
