import sys
from socket import *
from utils import *
from time import sleep

# Constants
RECEIVER_WINDOW = 15
# TODO: HIGHER TIMEOUT THAN 0.4 TO MAKE IT NOT TIME OUT WITH PACKET LOST
TIMEOUT = 1
# TODO: Check if how you should do this constant, bad practice to not have input in to function??


def establish_connection(server_socket, window):
    """
    Establishes connection with a client. Waits for SYN packet and response with SYN-ACK.
    Connection is established if ACK is received.
    :param server_socket: Socket of the server.
    :param window: Size of the receiver window to be sent to the client.
    """
    packet, client_address = server_socket.recvfrom(1000)
    _seq_num, _ack_num, flags, _window, _data = parse_packet(packet)
    server_socket.settimeout(TIMEOUT)

    if Flag.SYN == flags:
        print("SYN packet is received")
        sleep(0.2)
        server_socket.sendto(create_packet(0, 0, Flag.SYN | Flag.ACK, window), client_address)
        print("SYN-ACK packet is sent")

    else:
        print("Received packet missing SYN flag")

    packet, client_address = server_socket.recvfrom(1000)
    _seq_num, _ack_num, flags, _window, _data = parse_packet(packet)

    if Flag.ACK == flags:
        print("ACK packet is received")
        print("Connection Established\n")
    else:
        print("Received packet missing ACK flag")

# TODO: Maybe split out methods for taking data and closing connection?
# TODO: Maybe close connection as its own method?
def server(server_ip, port, discard_packet):
    """
    Runs the server part of the application. Listens for incoming connections to accept a file.
    Accepts Go-Back-N strategy. Closes connection on the clients request.
    :param server_ip:
    :param port: Port that the server will listen to
    :param discard_packet: Sequence number of the packet that should be discarded once
    """
    server_socket = socket(AF_INET, SOCK_DGRAM)
    try:
        server_socket.bind((server_ip, port))
    except OSError as e:
        print(f"Binding failed with port {port}, Error: {e}")
        sys.exit()

    # TODO: Should it be ready to wait for a new one after one closes?
    while True:
        establish_connection(server_socket, RECEIVER_WINDOW)

        next_seq_num = 1
        file_handler = FileHandler("test2.txt")
        # Checks if the connection is ready to close. Responds with FIN ACK if so, then closes. Otherwise, treats the data
        while True:
            packet, client_address = server_socket.recvfrom(1000)
            seq_num, _ack_num, flags, _window, data = parse_packet(packet)

            if flags == 0:
                # Ignores the packet once if the sequence number matches the one that should be discarded
                if seq_num == discard_packet:
                    discard_packet = -1
                    continue

                if seq_num == next_seq_num:
                    print(f"{time_now_log()} packet = {seq_num} is received")
                    file_handler.write_to_file(data)
                    next_seq_num += 1
                    server_socket.sendto(create_packet(0, seq_num, Flag.ACK, 0), client_address)
                    print(f"{time_now_log()} ACK for packet = {seq_num} sent")
                else:
                    print(f"{time_now_log()} out-of-order packet {seq_num} is received")


            elif Flag.FIN == flags:
                print("\nFIN packet is received")
                sleep(0.2)
                server_socket.sendto(create_packet(0, 0, Flag.FIN | Flag.ACK, 0), client_address)
                print("FIN-ACK packet is sent")

                # Sets timeout so it can listen for a new connection without error
                server_socket.settimeout(None)
                print("\nCalculated throughput that haven't been calculated yet")
                print("Connection Closed\n")
                break
        file_handler.close_file() # TODO: Maybe mobe to another place
    # TODO: Should socket be closed every time a connection is finished?
    server_socket.close()
    print("\nExiting server")
    sys.exit()
