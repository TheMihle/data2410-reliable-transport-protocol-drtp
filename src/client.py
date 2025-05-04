import sys
from socket import *
from utils import *
from time import sleep

# Constants
TIMEOUT = 0.4


def establish_connection(client_socket, server_address, port):
    # TODO: Check if SYN connection establishment work as it should
    #       What if one of the packets is dropped?
    print("Connection Establishment Phase:\n")
    client_socket.sendto(create_packet(1, 0, Flag.SYN, 0), (server_address, port))
    client_socket.settimeout(TIMEOUT)
    print("SYN packet is sent")

    packet = client_socket.recv(1000)
    _seq_num, _ack_num, flags, window, _data = parse_packet(packet)

    if Flag.SYN | Flag.ACK in Flag(flags):
        print("SYN-ACK packet is received")
        sleep(0.2)
        client_socket.sendto(create_packet(0, 0, Flag.ACK, 0), (server_address, port))
        print("ACK packet is sent")
        print("Connection established\n")
    else:
        print("Received packet missing SYN or ACK flag")
    return window


def send_data(client_socket, server_address, port, seq_num, sender_window, receiver_window):
    # TODO: Send data packets, just testing currently
    # TODO: use the window
    window = min(sender_window, receiver_window)

    while seq_num < 100:
        try:
            client_socket.sendto(create_packet(seq_num, 0, 0, 0), (server_address, port))
            print(
                f"{time_now_log()} packet with seq = {seq_num} is sent, sliding window = XXXXXX")

            # TODO: Like this or one line?
            packet = client_socket.recv(1000)
            _seq_num, ack_num, flags, _window, data = parse_packet(packet)

            if Flag.ACK in Flag(flags):
                seq_num += 1
                print(f"{time_now_log()} ACK packet with seq = {seq_num} received")

            else:
                print(f"Error, packet with seq_num {seq_num} may have been lost")
        except timeout:
            print(f"{time_now_log()} RTO occurred")
            continue
        #  TODO: Retransmission should have different log message

        sleep(0.05)



def close_connection(client_socket, server_address, port):
    # TODO: Check if closing connection work as it should both server and client
    #       What if FIN ACK isnt received?
    print("\nConnection Teardown:\n")
    client_socket.sendto(create_packet(0, 0, Flag.FIN, 0), (server_address, port))
    print("FIN packet is sent")

    message = client_socket.recv(1000)
    _seq_num, _ack_num, flags, _window, _data = parse_packet(message)

    if Flag.FIN | Flag.ACK in Flag(flags):
        print("FIN ACK packet is received")
        print("Connection closes")


def client(server_address, port, sender_window, file_name):
    """
    Runs the client part of the application
    :param server_address: IP of the server that should be connected to
    :param port:
    :param sender_window: Size of the sender window, number of packets can be handled at once
    :param file_name: File name of the file that should be transferred.
    """

    client_socket = socket(AF_INET, SOCK_DGRAM)

    receiver_window = establish_connection(client_socket, server_address, port)

    send_data(client_socket, server_address, port, 1, receiver_window, sender_window)

    close_connection(client_socket, server_address, port)

    print("\nExiting client")
    sys.exit()
