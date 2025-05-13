import sys
from random import randint
from socket import *
from time import time
from utils import *


class Server:
    """
    Server for the DRTP protocol. Listens for incoming connections to accept a file.
    Accepts Go-Back-N strategy. Closes connection on the clients request.
    """
    # Constants
    TIMEOUT = 1
    RECEIVER_WINDOW = 15

    def __init__(self, server_ip, server_port, discard_packet):
        """
        Initializes the server with the specified IP and port. Listens for incoming connections to accept a file.
        Accepts Go-Back-N strategy. Closes connection on the clients request.
        Initializes socket and FileHandler with filename.
        :param server_ip: IP address the server will listen to.
        :param server_port: Port number the server will listen to.
        :param discard_packet: Sequence number of the packet that should be discarded.
        """
        self.server_address = (server_ip, server_port)
        self.discard_packet = discard_packet
        self.socket = socket(AF_INET, SOCK_DGRAM)
        # So that the file name probably will be unique if tun multiple times
        self.file_handler = FileHandler(f"received_img_{randint(1, 99999999)}.jpg")
        self.data_start_time = None
        self.cumulative_data = 0

    def establish_connection(self) -> None:
        """
        Establishes connection with a client. Waits for SYN packet and response with SYN-ACK.
        Connection is established if ACK is received.
        :param self: Variables of the object itself.
        """
        print("Ready to accept connection\n")
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
            print("ACK packet is received\n"
                  "Connection Established\n")
        else:
            print("Received packet missing ACK flag")

    def accept_data(self, start_seq_num=1) -> None:
        """
        Listens and accepts incoming data packets. Checks of they arrive in the correct order
        and responds with ACK if it does. Starts closing the connection when FIN packet is received.
        :param self: Variables of the object itself.
        :param start_seq_num: Sequence number that the transfer should start on. Default is 1.
        """
        next_seq_num = start_seq_num
        self.data_start_time = time()   # For throughput calculation

        # Treats packets with no flags as a data packet. If a FIN flag is received, start closing the connection.
        while True:
            packet, client_address = self.socket.recvfrom(1000)
            seq_num, _ack_num, flags, _window, data = parse_packet(packet)

            if flags == 0:
                # Ignores the packet once if the sequence number matches the one that should be discarded
                if seq_num == self.discard_packet:
                    self.discard_packet = -1
                    continue

                # If it's the correct packet, write to the file and respond with ACK.
                if seq_num == next_seq_num:
                    self.cumulative_data += len(packet)     # For throughput calculation

                    print(f"{time_now_log()} packet = {seq_num} is received")
                    self.file_handler.write_to_file(data)
                    next_seq_num += 1

                    self.socket.sendto(create_packet(0, seq_num, Flag.ACK, 0), client_address)
                    print(f"{time_now_log()} ACK for packet = {seq_num} sent")
                else:
                    print(f"{time_now_log()} out-of-order packet {seq_num} is received")

            elif Flag.FIN == flags:
                self.close_connection(client_address)
                break

    def close_connection(self, client_address) -> None:
        """
        Finishes closing the connection by responding with an FIN-ACK packet.
        Calculates and outputs the throughput.
        :param self: Variables of the object itself.
        :param client_address: IP address and port number of the client that server is connected to.
                Tuple with (ip, port).
        """
        print("\nFIN packet is received")
        self.socket.sendto(create_packet(0, 0, Flag.FIN | Flag.ACK, 0), client_address)
        print("FIN-ACK packet is sent")

        throughput = (self.cumulative_data / (time() - self.data_start_time)) * 8 / 1e6
        print(f"\nThe throughput was {format(throughput, ".2f")} Mb/s\n"
              "Connection Closed\n")

    def exit_server(self, exit_code=0) -> None:
        """
        Closes the server's file handler and socket before exiting the server.
        :param self: Variables of the object itself.
        :param exit_code: The exit code that should happen when exiting.
        """
        self.file_handler.close_file()
        self.socket.close()
        print("Exiting server")
        sys.exit(exit_code)

    def run(self) -> None:
        """
        Runs the server part of the application. Listens for incoming connections to accept a file.
        Accepts Go-Back-N strategy. Closes connection on the clients request.
        :param self: Variables of the object itself.
        """

        try:
            self.socket.bind(self.server_address)
        except OSError as e:
            print(f"Binding failed with port {self.server_address[1]}, Error: {e}")
            self.exit_server(1)

        self.establish_connection()

        self.accept_data()

        self.exit_server()
