import argparse


# Argument parsing
# Custom type for parser to
# Can not have max limit
def range_check_int(min_int, max_int=None):
    def range_check(value):
        try:
            integer = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f'Integer expected, got {type(value)}')

        if integer < min_int or (max_int is not None and integer > max_int):
            raise argparse.ArgumentTypeError(f'{value} is an out of range, must be in range [{min_int}, {max_int}]')
        return integer
    return range_check


parser = argparse.ArgumentParser(
    description="Application for DRTP Reliable Transfer Protocol. Can be run as server or client "
                "to transfer file from client to server")
param_group = parser.add_mutually_exclusive_group(required=True)
param_group.add_argument('-s', '--server', dest="server", action="store_true",
                         help="Run the application in server mode, mutually exclusive with client")
param_group.add_argument('-c', '--client', dest="server", action="store_false",
                         help="Run the application in client mode, mutually exclusive with server")
parser.add_argument('-i', '--ip', dest="server_address", type=str, default="127.0.0.1",
                    help="IP address that is going to be used/is used for the server (default: 127.0.0.1)")
parser.add_argument('-p', '--port', dest="port", type=range_check_int(1024, 65535), default=8088,
                    help="Port that is going to be used (default: 8088)")
parser.add_argument('-f', '--file', dest="file_name", type=str, default="",
                    help="Name of the file that is to be transferred from client to server, does nothing for server")
parser.add_argument('-w', '--window', dest="window", type=range_check_int(1), default=3,
                    help="Size of the sender/receiver window for the client/server (default: 3)")
parser.add_argument('-d', '--discard', dest="discard_packet", type=int, default=-1,
                    help="Packet seq number of the packet that should be discarded by server, "
                         "does nothing for client (default: -1)")
param = parser.parse_args()

# TODO: c and s option, maybe enum og something similar
#       Maybe different default ip address
#       default of d should be infinity, how do you do that? negative number?


# TODO: Rest of the code

# TODO: Check if you should have the _main_ thing going on in this file
# TODO: check if you should more than one file
