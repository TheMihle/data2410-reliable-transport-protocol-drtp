import sys
from socket import *
from utils import *
from time import sleep

# TODO: Docstring needs update after changing it to a class
class Client:
    """


    """
    # Constants
    TIMEOUT = 0.4

    def __init__(self, server_ip, port, sender_window, file_name):
        """

        :param server_ip:
        :param port:
        :param sender_window:
        :param file_name:
        """
        self.server_address = (server_ip, port)
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.file_handler = FileHandler(file_name, 992)
        self.window_size = sender_window


    def establish_connection(self):
        """
        Establishes connection with the server via sending an SYN.
        Then waiting for SYN-ACK and responding with ACK.
        :param server_address: Address of the server to establish connection with.
                Tuple with (ip, port).
        :return: Window size of the receiver/server.
        """
        # TODO: Check if SYN connection establishment work as it should
        #       What if one of the packets is dropped?
        print("Connection Establishment Phase:\n")
        self.socket.sendto(create_packet(1, 0, Flag.SYN, 0), self.server_address)
        self.socket.settimeout(self.TIMEOUT)
        print("SYN packet is sent")

        packet = self.socket.recv(1000)
        _seq_num, _ack_num, flags, receiver_window, _data = parse_packet(packet)

        # TODO: IT CONTINUES EVEN IF THIS FLAG FAILS
        if Flag.SYN | Flag.ACK == flags:
            print("SYN-ACK packet is received")
            sleep(0.2)
            self.socket.sendto(create_packet(0, 0, Flag.ACK, 0), self.server_address)
            print("ACK packet is sent")
            print("Connection established\n")
        else:
            print("Received packet missing SYN or ACK flag\n")
        self.window_size = min(self.window_size, receiver_window)


    def send_window(self, window, file_handler, retransmission=False):
        """
        Sends all packets in the specified window. Can specify if its retransmission or not,
        makes a different console message.
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
            self.socket.sendto(create_packet(seq_num, 0, 0, 0, file_handler.get_file_data(seq_num)), self.server_address)
            sent_window.append(seq_num)
            print(f"{time_now_log()} packet with seq = {seq_num} is {tran_type}, sliding window = {sent_window}")


    def send_data(self, seq_num):
        """
        Sends the file to the receiver using the Go-Back-N strategy. Uses the smallest sliding window
        of client and receiver
        :param server_address: Address of the server to establish connection with.
                Tuple with (ip, port).
        :param seq_num: Sequence number that the transfer should start on.
        :param sender_window: Window size of the client.
        :param receiver_window: Window size of the receiver/server.
        :param file_name: Filename of the file that should be transferred.
        """
        next_ack = seq_num
        last_data_packet = float("inf")      # Temp value just so it compares true with an int


        self.send_window(range(next_ack , min(next_ack + self.window_size, last_data_packet + 1)), self.file_handler)

        while True:
            try:
                # TODO: Like this or one line?
                packet = self.socket.recv(1000)
                _seq_num, ack_num, flags, _window, data = parse_packet(packet)

                if Flag.ACK == flags and ack_num == next_ack:
                    print(f"{time_now_log()} ACK for packet = {ack_num} is received")
                    next_ack += 1

                    if next_ack + self.window_size - 1 <= last_data_packet:
                        data = self.file_handler.get_file_data(next_ack + self.window_size - 1)
                    if last_data_packet == float('inf') and data == b"":
                        last_data_packet = next_ack + self.window_size - 2
                    if next_ack + self.window_size - 1 <= last_data_packet:
                        self.socket.sendto(create_packet(next_ack + self.window_size - 1, 0, 0, 0, data), self.server_address)
                        print(f"{time_now_log()} packet with seq = {next_ack + self.window_size - 1} is sent, sliding window = {list(range(next_ack, min(next_ack + self.window_size, last_data_packet)))}")
                    if next_ack > last_data_packet: break

                else:
                    print(f"Error, packet with wrong flag or wrong ack number received")
            except timeout:
                print(f"{time_now_log()} RTO occurred")
                self.send_window(range(next_ack, min(next_ack + self.window_size, last_data_packet + 1)), self.file_handler, True)

            sleep(0.04)
        self.file_handler.close_file()


    def close_connection(self):
        """
        Closes the connection by sending a FIN packet to the receiver. Then waits for a
        FIN-ACK packet to confirm closing the connection.
        :param server_address: Address of the server to establish connection with.
                Tuple with (ip, port).
        """
        # TODO: Check if closing connection work as it should both server and client
        #       What if FIN ACK isnt received?
        # TODO: What if the package received doesn't have the right flag error?
        print("\nConnection Teardown:\n")
        # Send FIN packet
        self.socket.sendto(create_packet(0, 0, Flag.FIN, 0), self.server_address)
        print("FIN packet is sent")

        # Receive and check for FIN-ACK packet. Close if so.
        packet = self.socket.recv(1000)
        _seq_num, _ack_num, flags, _window, _data = parse_packet(packet)

        if Flag.FIN | Flag.ACK == flags:
            print("FIN ACK packet is received")
            print("Connection closes")


    def run(self):
        """
        Runs the client part of the application. Establishes a connection with the server and sends
        a file with Go-Back-N strategy before closing the connection.
        :param server_address: IP of the server that should be connected to.
        :param server_port: Port number on the server that should be connected to.
        :param sender_window: Size of the sender window, number of packets can be handled at once
        :param file_name: File name of the file that should be transferred.
        """
        self.establish_connection()

        # TODO: Maybe specifying start sequence number is not needed
        self.send_data(1)

        self.close_connection()

        print("\nExiting client")
        sys.exit()
