import argparse
import sys
from client import client
from server import server


# Argument parsing
# Custom type for parser, range check with int
def range_check_int(min_int, max_int=None):
    """
    Custom type for argparse. Checks if the input value is and int, and if it's
    between the minimum and optional maximum int provided.
    :param min_int: Minimum allowed value.
    :param max_int: Maximum allowed value. If not provided, no maximum value.
    :returns: Function that returns the valid int.
    :raises argparse ArgumentTypeError: If the value is out of range or not an int.
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
# TODO: Maybe different default ip address
# TODO: Default of d should be infinity, how do you do that? negative number?
# TODO: Check if the dest is actually needed
# TODO: Add docstring/comment
# TODO: Check out annotation for return type/ type hints
# TODO: Maybe add check and print a message if an parameter is not used
#           for example if you use discard on the client or (address on server?)
# TODO: Fix so that connection from other clients is rejected and the first one continues

# TODO: Rest of the code
# TODO: check if you should use classes for server and client
# TODO: Check the ports, should be the same on both sides when on mininet? have to bind first on client side too


def main():
    """
    Activates the server or client based on the input arguments
    """
    try:
        args = get_arguments()
        if args.server:
            server(args.server_address, args.port, args.window, args.discard_packet)
        elif args.client:
            client(args.server_address, args.port, args.window, args.file_name)
    except KeyboardInterrupt:
        print("Exiting because from Keyboard Interrupt")
        sys.exit()


if __name__ == "__main__":
    main()

    # TODO: Remove these temp testing
    # print(datetime.now().strftime("%H:%M:%S.%f"))
