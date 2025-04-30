import argparse
import sys
from datetime import datetime
from enum import IntFlag
from socket import *
from struct import pack, unpack
from time import sleep


# Argument parsing
# Custom type for parser, range check with int
def range_check_int(min_int, max_int=None):
    """
    Custom type for argparse. Checks if input value is and int, and if its between
    the minimum and optional maximum int provided.
    :param min_int: Minimum allowed value.
    :param max_int: Maximum allowed value. If not provided, no maximum value.
    :returns: function that returns the valid int.
    :raises argparse ArgumentTypeError: If value is out of range or not an int.
    """
    def range_check(value):
        try:
            integer = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f'Integer expected, got {type(value)}')

        if integer < min_int or (max_int is not None and integer > max_int):
            raise argparse.ArgumentTypeError(f'{value} is an out of range, must be in range [{min_int}, {max_int}]')
        return integer

    return range_check


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Application for DRTP Reliable Transfer Protocol. Can be run as server or client "
                    "to transfer file from client to server")
    args_group = parser.add_mutually_exclusive_group(required=True)
    args_group.add_argument('-s', '--server', action="store_true",
                            help="Run the application in server mode, mutually exclusive with client")
    args_group.add_argument('-c', '--client', action="store_true",
                            help="Run the application in client mode, mutually exclusive with server")
    parser.add_argument('-i', '--ip', dest="server_address", type=str, default="127.0.0.1",
                        help="IP address that is going to be used/is used for the server (default: 127.0.0.1)")
    parser.add_argument('-p', '--port', type=range_check_int(1024, 65535), default=8088,
                        help="Port that is going to be used (default: 8088)")
    parser.add_argument('-f', '--file', dest="file_name", type=str, default="",
                        help="Name of the file that is to be transferred from client to server, does nothing for server")
    parser.add_argument('-w', '--window', type=range_check_int(1), default=3,
                        help="Size of the sender/receiver window for the client/server (default: 3)")
    parser.add_argument('-d', '--discard', dest="discard_packet", type=int, default=-1,
                        help="Packet seq number of the packet that should be discarded by server, "
                             "does nothing for client (default: -1)")
    return parser.parse_args()


# TODO: c and s option, maybe enum og something similar
#       Maybe different default ip address
#       default of d should be infinity, how do you do that? negative number?
#       Check if the dest is actually needed
#       Add docstring/comment
#       Check out annotation for return type/ type hints


# TODO: Rest of the code
# TODO: check if you should more than one file
# TODO: Check the ports, should be the same on both sides when on mininet? have to bind first on client side too

class Flag(IntFlag):
    """
    Flags for the header of the DRTP protocol
    Reset, ACK, SYN, FIN
    Syntax for multiple flags: Flag.ACK | Flag.SYN
    """
    RESET = 1
    ACK = 2
    SYN = 4
    FIN = 8


def create_packet(seq_num, ack_num, flags, window):
    header_format = "!HHHH"

    header = pack(header_format, seq_num, ack_num, flags, window)
    packet2 = header
    return packet2


def read_packet(packet) -> tuple:
    header_format = "!HHHH"
    packet = unpack(header_format, packet[:8])  # Reads only the header
    return packet[0], packet[1], packet[2], packet[3]


def client(args):
    """
    Runs the client part of the application
    :param args:
    """
    data = create_packet(1, 0, Flag.SYN, args.window)
    client_socket = socket(AF_INET, SOCK_DGRAM)

    # TODO: Check if SYN connection establushment work as it should
    #       What if one of the packets is dropped?
    print("Connection Establishment Phase:\n")
    client_socket.sendto(data, (args.server_address, args.port))
    client_socket.settimeout(0.4)
    print("SYN packet is sent")

    message = client_socket.recv(1000)
    seq_num, ack_num, flags, window = read_packet(message)

    if Flag.SYN | Flag.ACK in Flag(flags):
        print("SYN-ACK packet is received")
        sleep(0.2)
        client_socket.sendto(create_packet(0, ack_num, Flag.ACK, args.window), (args.server_address, args.port))
        print("ACK packet is sent")
        print("Connection established\n")
    else:
        print("Received packet missing SYN or ACK flag")

    # TODO: Send data packets, just testing currently

    while seq_num < 5:
        seq_num += 1
        client_socket.sendto(create_packet(seq_num, ack_num, 0, args.window), (args.server_address, args.port))
        print(
            f"{datetime.now().strftime("%H:%M:%S.%f")} -- packet with seq = {seq_num} is sent, sliding window = XXXXXX")

        message = client_socket.recv(1000)
        seq_num, ack_num, flags, window = read_packet(message)

        if Flag.ACK in Flag(flags):
            print(f"Packet with seq = {seq_num} recived")

        else:
            print(f"Error, packet with seq_num {seq_num} may have been lost")

        sleep(0.2)

    # TODO: Check if closing connection work as it should both server and cient
    #       What if FIN ACK isnt recived?
    # Closing the connection
    print("\nConnection Teardown:\n")
    client_socket.sendto(create_packet(0, ack_num, Flag.FIN, args.window), (args.server_address, args.port))
    print("FIN packet is sent")

    message = client_socket.recv(1000)
    seq_num, ack_num, flags, window = read_packet(message)

    if Flag.FIN | Flag.ACK in Flag(flags):
        print("FIN ACK packet is received")
        print("Connection closes")

    print("\nExiting client")
    sys.exit()


def server(args):
    """
    Runs the server part of the application
    :param args:
    """
    server_socket = socket(AF_INET, SOCK_DGRAM)
    try:
        server_socket.bind(('', args.port))
    except OSError as e:
        print(f"Binding failed with port {args.port}, Error: {e}")
        sys.exit()

    message, (client_address, client_port) = server_socket.recvfrom(1000)
    seq_num, ack_num, flags, window = read_packet(message)
    server_socket.settimeout(0.4)

    if Flag.SYN in Flag(flags):
        print("SYN packet is received")
        sleep(0.2)
        server_socket.sendto(create_packet(0, ack_num, Flag.SYN | Flag.ACK, args.window), (client_address, client_port))
        print("SYN-ACK packet is sent")

    else:
        print("Received packet missing SYN flag")

    message, (client_address, client_port) = server_socket.recvfrom(1000)
    seq_num, ack_num, flags, window = read_packet(message)

    if Flag.ACK in Flag(flags):
        print("ACK packet is received")
        print("Connection Established\n")
        sleep(0.2)
    else:
        print("Received packet missing ACK flag")

    # Checks if connection is ready to close. Responds with FIN ACK if so then closes. Otherwise, treats the data
    while True:
        message, (client_address, client_port) = server_socket.recvfrom(1000)
        seq_num, ack_num, flags, window = read_packet(message)

        if flags == 0:
            print(f"{datetime.now().strftime("%H:%M:%S.%f")} -- packet {seq_num} is received")
            sleep(0)
            server_socket.sendto(create_packet(seq_num, ack_num, Flag.ACK, args.window), (client_address, client_port))
            print(f"ACK for packet with seq = {seq_num} sent")

        elif Flag.FIN in Flag(flags):
            print("\nFIN packet is received")
            server_socket.sendto(create_packet(0, ack_num, Flag.FIN | Flag.ACK, args.window),
                                 (client_address, client_port))
            print("FIN-ACK packet is sent")
            server_socket.close()

            print("\nCalculated throughput that haven't been calculated yet")
            print("Connection Closes")
            break

    print("\nExiting server")
    sys.exit()


def main():
    """
    Activates the server or client based on the input arguments
    """
    try:
        args = get_arguments()
        if args.server:
            server(args)
        elif args.client:
            client(args)
    except KeyboardInterrupt:
        print("Exiting from Keyboard Interrupt")
        sys.exit()


if __name__ == "__main__":
    main()

    # TODO: Remove these temp testing

    #print(read_packet(create_packet(1, 1, Flag.ACK | Flag.SYN, 1)))
    # print(datetime.now().strftime("%H:%M:%S.%f"))
