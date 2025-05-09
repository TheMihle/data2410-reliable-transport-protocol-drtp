import argparse
import ipaddress
import sys
from os import access, R_OK
from os.path import isfile
from client import client
from server import server


# Argument parsing
# Custom types
def range_check_int(min_int, max_int=None):
    """
    Custom type for argparse. Checks if the input value is and int, and if it's
    between the minimum and optional maximum int provided.
    :param min_int: Minimum allowed value.
    :param max_int: Maximum allowed value. If not provided, no maximum value.
    :return: Function that returns the valid int.
    :raises argparse ArgumentTypeError: If the value is out of range or not an int.
    """
    def range_check(value):
        try:
            integer = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Integer expected, got {type(value)}")

        if integer < min_int or (max_int is not None and integer > max_int):
            raise argparse.ArgumentTypeError(f"{value} is an out of range, must be in range [{min_int}, {max_int}]")
        return integer
    return range_check


def ip_address(ip):
    """
    Custom type for argparse. Checks if the input address is a valid IPv4 address.
    :param ip: IP address to be checked.
    :return: Accepted IP address.
    :raises argparse ArgumentTypeError: If the address is an IPv6 address or otherwise not an IPv4 address.
    """
    try:
        if ipaddress.ip_address(ip).version == 6:
            raise argparse.ArgumentTypeError(f"{ip} is a IPv6 address, not a valid IPv4 address")
    except ValueError:
        raise argparse.ArgumentTypeError(f"{ip} is not a valid IP address")
    return ip


# TODO: Add filetype check to file
def file_name_check(file_name):
    """
    Custom type for argparse. Check if the file exists and is readable.
    :param file_name: Name of the file to be checked.
    :return: Filename as a string.
    :raises argparse ArgumentTypeError: If the file does not exist or is not readable.
    """
    if file_name == "": return file_name
    if not isfile(file_name) or not access(file_name, R_OK):
        raise argparse.ArgumentTypeError(f"{file_name} does not exist or is not readable")
    return str(file_name)


# Parser function
def get_arguments():
    """
    Parses the input arguments for the application.
    See argument help for specifics about each argument.
    Checks if arguments are valid and notifies if they are ignored.
    :return: Argument object with parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Application for DRTP Reliable Transfer Protocol. Can be run as server or client "
                    "to transfer file from client to server with Go-Back-N strategy.")
    args_group = parser.add_mutually_exclusive_group(required=True)
    args_group.add_argument('-s', '--server', action="store_true",
                            help="Run the application in server mode, mutually exclusive with client")
    args_group.add_argument('-c', '--client', action="store_true",
                            help="Run the application in client mode, mutually exclusive with server")
    parser.add_argument('-i', '--ip', dest="server_ip", type=ip_address, default="127.0.0.1",
                        help="IPv4 address that is going to be used/is used for the server (default: 127.0.0.1)")
    parser.add_argument('-p', '--port', type=range_check_int(1024, 65535), default=8088,
                        help="Port that is going to be used, port of the server. (default: 8088)")
    parser.add_argument('-f', '--file', dest="file_name", type=file_name_check, default="",
                        help="Name of the file that is to be transferred from client to server, ignored by the server")
    parser.add_argument('-w', '--window', type=range_check_int(1), default=3,
                        help="Size of the sender window for the client, ignored by server. (default: 3)")
    parser.add_argument('-d', '--discard', dest="discard_packet", type=int, default=-1,
                        help="Packet seq number of the packet that should be discarded by server, "
                             "ignored by client. (default: -1)")
    args = parser.parse_args()

    # Information message if arguments are ignored
    if args.server and args.file_name != "": print("Server doesnt use file name, ignoring.")
    if args.server and args.window != 3: print("Server doesnt use window argument, ignoring.")
    if args.client and args.discard_packet != -1: print("Client doesnt use discard argument, ignoring.")
    print("")
    return args


# TODO: Check if the dest is actually needed
# TODO: Add docstring/comment
# TODO: Check out annotation for return type/ type hints
# TODO: Fix so that connection from other clients is rejected and the first one continues

# TODO: check if you should use classes for server and client
# TODO: Should fin and fin ack have sequence numbers
# TODO: Own method for close connection?
# TODO sys exit (1) instead if just sys exit?
# TODO: Set up requirement for -f flag for client
# TODO: Connection refused error needed or just timeout?
# TODO: Should there be no capital letters in docstring and argparse?
# TODO: Rest of the code


def main():
    """
    Activates the server or client based on the input arguments.
    """
    try:
        args = get_arguments()
        if args.server:
            server(args.server_ip, args.port, args.discard_packet)
        elif args.client:
            client(args.server_ip, args.port, args.window, args.file_name)
    except KeyboardInterrupt:
        print("Exiting because from Keyboard Interrupt")
        sys.exit()


if __name__ == "__main__":
    main()

    # print(f"{set(range(1, min(4,6)))}")
