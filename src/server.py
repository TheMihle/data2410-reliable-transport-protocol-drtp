import sys
from socket import *
from utils import *


# TODO: Docstring needs update after changing it to a class
class Server:
    """

    """
    # Constants
    TIMEOUT = 1
    RECEIVER_WINDOW = 15

    def __init__(self, server_ip, port, discard_packet):
        """

        :param server_ip:
        :param port:
        :param discard_packet:
        """
        self.server_address = (server_ip, port)
        self.discard_packet = discard_packet
        self.file_handler = None
        self.socket = socket(AF_INET, SOCK_DGRAM)


    def establish_connection(self):
        """
        Establishes connection with a client. Waits for SYN packet and response with SYN-ACK.
        Connection is established if ACK is received.
        :param window: Size of the receiver window to be sent to the client.
        """
        packet, client_address = self.socket.recvfrom(1000)
        _seq_num, _ack_num, flags, _window, _data = parse_packet(packet)
        self.socket.settimeout(self.TIMEOUT)

        if Flag.SYN == flags:
            print("SYN packet is received")
            self.socket.sendto(create_packet(0, 0, Flag.SYN | Flag.ACK, self.RECEIVER_WINDOW), client_address)
            print("SYN-ACK packet is sent")

        else:
            print("Received packet missing SYN flag")

        packet, client_address = self.socket.recvfrom(1000)
        _seq_num, _ack_num, flags, _window, _data = parse_packet(packet)

        if Flag.ACK == flags:
            print("ACK packet is received")
            print("Connection Established\n")
        else:
            print("Received packet missing ACK flag")

    # TODO: Maybe split out methods for taking data and closing connection?
    # TODO: Maybe close connection as its own method?
    def run(self):
        """
        Runs the server part of the application. Listens for incoming connections to accept a file.
        Accepts Go-Back-N strategy. Closes connection on the clients request.
        :param self.server_address:
        :param port: Port that the server will listen to
        :param discard_packet: Sequence number of the packet that should be discarded once
        """

        try:
            self.socket.bind(self.server_address)
        except OSError as e:
            print(f"Binding failed with port {self.server_address[1]}, Error: {e}")
            sys.exit(1)

        # TODO: Should it be ready to wait for a new one after one closes?
        while True:
            self.establish_connection()

            next_seq_num = 1
            self.file_handler = FileHandler("test2.txt")
            # Checks if the connection is ready to close. Responds with FIN ACK if so, then closes. Otherwise, treats the data
            while True:
                packet, client_address = self.socket.recvfrom(1000)
                seq_num, _ack_num, flags, _window, data = parse_packet(packet)

                if flags == 0:
                    # Ignores the packet once if the sequence number matches the one that should be discarded
                    if seq_num == self.discard_packet:
                        self.discard_packet = -1
                        continue

                    if seq_num == next_seq_num:
                        print(f"{time_now_log()} packet = {seq_num} is received")
                        self.file_handler.write_to_file(data)
                        next_seq_num += 1
                        self.socket.sendto(create_packet(0, seq_num, Flag.ACK, 0), client_address)
                        print(f"{time_now_log()} ACK for packet = {seq_num} sent")
                    else:
                        print(f"{time_now_log()} out-of-order packet {seq_num} is received")


                elif Flag.FIN == flags:
                    print("\nFIN packet is received")
                    self.socket.sendto(create_packet(0, 0, Flag.FIN | Flag.ACK, 0), client_address)
                    print("FIN-ACK packet is sent")

                    # Sets timeout so it can listen for a new connection without error
                    self.socket.settimeout(None)
                    print("\nCalculated throughput that haven't been calculated yet")
                    print("Connection Closed\n")
                    break
            self.file_handler.close_file() # TODO: Maybe mobe to another place
        # TODO: Should socket be closed every time a connection is finished?
        self.socket.close()
        print("\nExiting server")
        sys.exit()
