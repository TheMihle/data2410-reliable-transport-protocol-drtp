import sys
from socket import *
from utils import *
from time import sleep

# Constants
TIMEOUT = 0.4


def establish_connection(client_socket, server_address):
    """
    Establishes connection with the server via sending an SYN.
    Then waiting for SYN-ACK and responding with ACK.
    :param client_socket: Socket of the client.
    :param server_address: Address of the server to establish connection with.
            Tuple with (ip, port).
    :return: Window size of the receiver/server.
    """
    # TODO: Check if SYN connection establishment work as it should
    #       What if one of the packets is dropped?
    print("Connection Establishment Phase:\n")
    client_socket.sendto(create_packet(1, 0, Flag.SYN, 0), server_address)
    client_socket.settimeout(TIMEOUT)
    print("SYN packet is sent")

    packet = client_socket.recv(1000)
    _seq_num, _ack_num, flags, window, _data = parse_packet(packet)

    # TODO: IT CONTINUES EVEN IF THIS FLAG FAILS
    if Flag.SYN | Flag.ACK == flags:
        print("SYN-ACK packet is received")
        sleep(0.2)
        client_socket.sendto(create_packet(0, 0, Flag.ACK, 0), server_address)
        print("ACK packet is sent")
        print("Connection established\n")
    else:
        print("Received packet missing SYN or ACK flag\n")
    return window


def send_window(client_socket, server_address, window, file_handler, retransmission=False):
    """
    Sends all packets in the specified window. Can specify if its retransmission or not,
    makes a different console message.
    :param client_socket: Socket of the client.
    :param server_address: Address of the server to establish connection with.
            Tuple with (ip, port).
    :param window: Window of packets that should be sent. List with sequence numbers.
    :param file_handler: File handler for the file that is written tp.
    :param retransmission: Boolean True if it's a retransmission.
    """
    if retransmission: tran_type = "retransmitted"
    else:  tran_type = "sent"
    sent_window = []
    for seq_num in window:
        client_socket.sendto(create_packet(seq_num, 0, 0, 0, file_handler.get_file_data(seq_num)), server_address)
        sent_window.append(seq_num)
        print(f"{time_now_log()} packet with seq = {seq_num} is {tran_type}, sliding window = {sent_window}")


def send_data(client_socket, server_address, seq_num, sender_window, receiver_window, file_name):
    """
    Sends the file to the receiver using the Go-Back-N strategy. Uses the smallest sliding window
    of client and receiver.
    :param client_socket: Socket of the client.
    :param server_address: Address of the server to establish connection with.
            Tuple with (ip, port).
    :param seq_num: Sequence number that the transfer should start on.
    :param sender_window: Window size of the client.
    :param receiver_window: Window size of the receiver/server.
    :param file_name: Filename of the file that should be transferred.
    """
    window_size = min(sender_window, receiver_window)
    next_ack = 1
    last_data_packet = float("inf")      # Temp value just so it compares true with an int

    file_handler = FileHandler(file_name, 992)

    send_window(client_socket, server_address, range(next_ack , min(next_ack + window_size, last_data_packet + 1)), file_handler)

    while True:
        try:
            # TODO: Like this or one line?
            packet = client_socket.recv(1000)
            _seq_num, ack_num, flags, _window, data = parse_packet(packet)

            if Flag.ACK == flags and ack_num == next_ack:
                print(f"{time_now_log()} ACK for packet = {ack_num} is received")
                next_ack += 1

                if next_ack + window_size - 1 <= last_data_packet:
                    data = file_handler.get_file_data(next_ack + window_size - 1)
                if last_data_packet == float('inf') and data == b"":
                    last_data_packet = next_ack + window_size - 2
                if next_ack + window_size - 1 <= last_data_packet:
                    client_socket.sendto(create_packet(next_ack + window_size - 1, 0, 0, 0, data), server_address)
                    print(f"{time_now_log()} packet with seq = {next_ack + window_size - 1} is sent, sliding window = {list(range(next_ack, min(next_ack + window_size, last_data_packet)))}")
                if next_ack > last_data_packet: break

            else:
                print(f"Error, packet with seq_num {seq_num} may have been lost")
        except timeout:
            print(f"{time_now_log()} RTO occurred")
            send_window(client_socket, server_address, range(next_ack, min(next_ack + window_size, last_data_packet + 1)), file_handler, True)

        sleep(0.04)
    file_handler.close_file()


def close_connection(client_socket, server_address):
    """
    Closes the connection by sending a FIN packet to the receiver. Then waits for a
    FIN-ACK packet to confirm closing the connection.
    :param client_socket: Socket of the client.
    :param server_address: Address of the server to establish connection with.
            Tuple with (ip, port).
    """
    # TODO: Check if closing connection work as it should both server and client
    #       What if FIN ACK isnt received?
    # TODO: What if the package received doesn't have the right flag error?
    print("\nConnection Teardown:\n")
    # Send FIN packet
    client_socket.sendto(create_packet(0, 0, Flag.FIN, 0), server_address)
    print("FIN packet is sent")

    # Receive and check for FIN-ACK packet. Close if so.
    packet = client_socket.recv(1000)
    _seq_num, _ack_num, flags, _window, _data = parse_packet(packet)

    if Flag.FIN | Flag.ACK == flags:
        print("FIN ACK packet is received")
        print("Connection closes")


def client(server_address, server_port, sender_window, file_name):
    """
    Runs the client part of the application. Establishes a connection with the server and sends
    a file with Go-Back-N strategy before closing the connection.
    :param server_address: IP of the server that should be connected to.
    :param server_port: Port number on the server that should be connected to.
    :param sender_window: Size of the sender window, number of packets can be handled at once
    :param file_name: File name of the file that should be transferred.
    """

    client_socket = socket(AF_INET, SOCK_DGRAM)

    receiver_window = establish_connection(client_socket, (server_address, server_port))

    # TODO: Maybe specifying start sequence number is not needed
    send_data(client_socket, (server_address, server_port), 1, receiver_window, sender_window, file_name)

    close_connection(client_socket, (server_address, server_port))

    print("\nExiting client")
    sys.exit()
