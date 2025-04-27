import argparse
import sys
from datetime import datetime
from enum import IntFlag
from socket import *
from struct import pack, unpack


# Argument parsing
# Custom type for parser to
# Can not have max limit
def range_check_int(min_int, max_int=None):
    """
    Custom type for argparse. Checks if input value is and int, and if its between
    the minimum int provided.
    :param min_int: Minimum allowed value
    :param max_int: Maximum allowed value. If not provided, no maximum value.
    :return:
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

class Flag(IntFlag):
    """
    Flags for the header of the DRTP protocol
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


def read_packet(packet):
    header_format = "!HHHH"
    packet = unpack(header_format, packet[:8])       # Reads only the header
    return packet[0], packet[1], packet[2], packet[3]


def client(args):
    data = create_packet(1, 0, Flag.ACK, args.window)
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.sendto(data, (args.server_address, args.port))


def server(args):
    server_socket = socket(AF_INET, SOCK_DGRAM)
    try:
        server_socket.bind(('', args.port))
    except OSError as e:
        print(f'Binding failed with port {args.port}, Error: {e}')
        sys.exit()

    while True:
        message, client_address = server_socket.recvfrom(1000)
        print(message)


def main():
    """
    Activates the server or client based on the input arguments
    """
    args = get_arguments()
    if args.server:
        server(args)
    elif args.client:
        client(args)


if __name__ == "__main__":
    main()

    # TODO: Remove these temp testing

    #print(read_packet(create_packet(1, 1, Flag.ACK | Flag.SYN, 1)))
    # print(datetime.now().strftime("%H:%M:%S.%f"))

