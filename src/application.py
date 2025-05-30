import argparse
import ipaddress
import sys
from argparse import Namespace
from os import access, R_OK
from os.path import isfile
from client import Client
from server import Server


# Argument parsing
# Custom types
def range_check_int(min_int: int, max_int: int = None):
    """
    Custom type for argparse. Checks if the input value is and int, and if it's
    between the minimum and optional maximum int provided.
    :param min_int: Minimum allowed value.
    :param max_int: Maximum allowed value. If not provided, no maximum value.
    :return: Function that returns the valid int.
    :raises argparse ArgumentTypeError: If the value is out of range or not an int.
    """
    def range_check(value: int | str) -> int:
        try:
            integer: int = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"Integer expected, got {type(value)}")

        if integer < min_int or (max_int is not None and integer > max_int):
            raise argparse.ArgumentTypeError(f"{value} is an out of range, must be in range [{min_int}, {max_int}]")
        return integer
    return range_check


def ip_address(ip: str) -> str:
    """
    Custom type for argparse. Checks if the input address is a valid IPv4 address.
    :param ip: IP address to be checked.
    :return: Accepted IP address.
    :raises argparse ArgumentTypeError: If the address is an IPv6 address, or otherwise not an IPv4 address.
    """
    try:
        if ipaddress.ip_address(ip).version == 6:
            raise argparse.ArgumentTypeError(f"{ip} is a IPv6 address, not a valid IPv4 address")
    except ValueError:
        raise argparse.ArgumentTypeError(f"{ip} is not a valid IP address")
    return ip


def file_name_check(file_name: str) -> str:
    """
    Custom type for argparse. Check if the file exists and is readable if it's provided.
    Also checks if the file is a correct file format. (.jpg, .JPG, .jpeg, .JPEG)
    :param file_name: Name of the file to be checked.
    :return: Filename as a string.
    :raises argparse ArgumentTypeError: If the file does not exist or is not readable.
    """
    if file_name == "": return file_name
    if not isfile(file_name) or not access(file_name, R_OK):
        raise argparse.ArgumentTypeError(f"{file_name} does not exist or is not readable")
    if not file_name.lower().endswith((".jpg",".jpeg")):
        raise argparse.ArgumentTypeError(f"{file_name} is not a valid image file type, must be jpg, jpeg")
    return str(file_name)


# Parser function
def get_arguments() -> Namespace:
    """
    Parses the input arguments for the application.
    See argument help for specifics about each argument.
    Checks if arguments are valid/allowed and notifies if they are ignored.
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
    parser.add_argument('-p', '--port', dest="server_port", type=range_check_int(1024, 65535), default=8088,
                        help="Port that is going to be used, port of the server. (default: 8088)")
    parser.add_argument('-f', '--file', dest="file_name", type=file_name_check, default="",
                        help="Name of the file that is to be transferred from client to server, ignored by the server.")
    parser.add_argument('-w', '--window', type=range_check_int(1), default=3,
                        help="Size of the sender window for the client, ignored by server. (default: 3)")
    parser.add_argument('-d', '--discard', dest="discard_packet", type=int, default=-1,
                        help="Packet seq number of the packet that should be discarded by server, "
                             "ignored by client. (default: -1)")
    args = parser.parse_args()

    # Check for filename when running as a client
    if args.client and args.file_name == "":
        print("Argument Error: Must specify file name of file to be transferred with -f flag on client, exiting.\n")
        sys.exit(1)

    # Information message if arguments are ignored
    if args.server and args.file_name != "": print("Server doesnt use file name, ignoring.")
    if args.server and args.window != 3: print("Server doesnt use window argument, ignoring.")
    if args.client and args.discard_packet != -1: print("Client doesnt use discard argument, ignoring.")
    print("")
    return args


def main() -> None:
    """
    Activates the server or client based on the input arguments.
    """
    args = get_arguments()
    if args.server:
        Server(args.server_ip, args.server_port, args.discard_packet).run()
    elif args.client:
        Client(args.server_ip, args.server_port, args.window, args.file_name).run()


if __name__ == "__main__":
    main()
