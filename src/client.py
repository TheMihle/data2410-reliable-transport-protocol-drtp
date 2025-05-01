import sys
from socket import *
from utils import *
from datetime import datetime
from time import sleep


def establish_connection(client_socket, server_address, port, window):
    # TODO: Check if SYN connection establishment work as it should
    #       What if one of the packets is dropped?
    print("Connection Establishment Phase:\n")
    data = create_packet(1, 0, Flag.SYN, window)
    client_socket.sendto(data, (server_address, port))
    client_socket.settimeout(0.4)
    print("SYN packet is sent")

    message = client_socket.recv(1000)
    seq_num, ack_num, flags, window = read_packet(message)

    if Flag.SYN | Flag.ACK in Flag(flags):
        print("SYN-ACK packet is received")
        sleep(0.3)
        client_socket.sendto(create_packet(0, ack_num, Flag.ACK, window), (server_address, port))
        print("ACK packet is sent")
        print("Connection established\n")
    else:
        print("Received packet missing SYN or ACK flag")
    return seq_num, ack_num, window


def send_data(client_socket, server_address, port,  seq_num, ack_num, window):
    # TODO: Send data packets, just testing currently

    while seq_num < 5:
        seq_num += 1
        client_socket.sendto(create_packet(seq_num, ack_num, 0, window), (server_address, port))
        print(
            f"{datetime.now().strftime("%H:%M:%S.%f")} -- packet with seq = {seq_num} is sent, sliding window = XXXXXX")

        message = client_socket.recv(1000)
        seq_num, ack_num, flags, window = read_packet(message)

        if Flag.ACK in Flag(flags):
            print(f"{datetime.now().strftime("%H:%M:%S.%f")} -- ACK packet with seq = {seq_num} received")

        else:
            print(f"Error, packet with seq_num {seq_num} may have been lost")

        sleep(0.2)

    return seq_num, ack_num, window


def close_connection(client_socket, server_address, port, seq_num, ack_num, window):
    # TODO: Check if closing connection work as it should both server and client
    #       What if FIN ACK isnt received?
    print("\nConnection Teardown:\n")
    client_socket.sendto(create_packet(0, ack_num, Flag.FIN, window), (server_address, port))
    print("FIN packet is sent")

    message = client_socket.recv(1000)
    seq_num, ack_num, flags, window = read_packet(message)

    if Flag.FIN | Flag.ACK in Flag(flags):
        print("FIN ACK packet is received")
        print("Connection closes")


def client(server_address, port, window, file_name):
    """
    Runs the client part of the application
    :param server_address: IP of the server that should be connected to
    :param port:
    :param window: Size of the sender window, number of packets can be handled at once
    :param file_name: File name of the file that should be transferred.
    """

    client_socket = socket(AF_INET, SOCK_DGRAM)

    seq_num, ack_num, window = establish_connection(client_socket, server_address, port, window)

    seq_num, ack_num, window = send_data(client_socket, server_address, port, seq_num, ack_num, window)

    close_connection(client_socket, server_address, port, seq_num, ack_num, window)

    print("\nExiting client")
    sys.exit()
