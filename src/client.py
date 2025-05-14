import sys
from socket import *
from utils import *
from time import sleep


class Client:
    """
    Client for the DRTP protocol. Connects to the server and sends a file with Go-Back-N strategy.
    Closes the connection when file transfer is complete.
    """
    # Constants
    TIMEOUT = 0.4

    def __init__(self, server_ip, server_port, sender_window, file_name):
        """
        Initialises the client. Connects to the server with the specified IP and port.
        Uses Go-Back-N strategy. Closes connection when the transfer is complete.
        Initialises socket and FileHandler with filename.
        :param server_ip: IP address of the server that the client should connect to.
        :param server_port: Port number on the server that the client should connect to.
        :param sender_window: The Maximum size of the sliding window the sender should send.
        :param file_name: Name of the file that should be transferred.
        """
        self.server_address = (server_ip, server_port)
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.file_handler = FileHandler(file_name, 992)
        self.window_size = sender_window

    def establish_connection(self) -> None:
        """
        Establishes connection with the server via sending an SYN. Then waiting for SYN-ACK to
        establish the connection and responding with ACK. Ignores wrong flags,
        Exits the client if an error is raised. Only returns on success.
        :param self: Variables of the object itself.
        """
        # TODO: Check if SYN connection establishment work as it should
        #       What if one of the packets is dropped?
        try:
            print("Connection Establishment Phase:\n")
            self.socket.sendto(create_packet(1, 0, Flag.SYN, 0), self.server_address)
            self.socket.settimeout(self.TIMEOUT)
            print("SYN packet is sent")

            # Waits for SYN | ACK ignores other packets
            while True:
                packet = self.socket.recv(1000)
                _seq_num, _ack_num, flags, receiver_window, _data = parse_packet(packet)

                if Flag.SYN | Flag.ACK == flags:
                    print("SYN-ACK packet is received")
                    self.socket.sendto(create_packet(0, 0, Flag.ACK, 0), self.server_address)
                    print("ACK packet is sent\n"
                          "Connection established\n")
                    break
                else:
                    print("Received packet missing SYN or ACK flag\n")

            # Chooses the smallest window size between the client and receiver.
            self.window_size = min(self.window_size, receiver_window)
        except timeout:
            print("\nError: Connection timed out while trying to establish connection")
            self.close_client(1)
        except ConnectionError:
            print("\nError: Connection refused by server while trying to establish connection")
            self.close_client(1)
        except OSError as e:
            print(f"\nError: {e}")
            self.close_client(1)

    # TODO: Stop if file is empty
    def send_window(self, window, retransmission=False) -> None:
        """
        Sends all packets in the specified window. Can specify if its retransmission, makes a different console message.
        :param self: Variables of the object itself.
        :param window: Window of packets that should be sent. List with sequence numbers.
        :param retransmission: Set True if it's a retransmission. Changes the console output.
        :raises ConnectionError: If the server refuses the packet.
        """
        if retransmission: tran_type = "retransmitted"
        else:  tran_type = "sent"
        sent_window = []
        for seq_num in window:
            self.socket.sendto(create_packet(seq_num, 0, 0, 0, self.file_handler.get_file_data(seq_num)), self.server_address)
            sent_window.append(seq_num)
            print(f"{time_now_log()} packet with seq = {seq_num} is {tran_type}, sliding window = {sent_window}")

    def send_data(self, start_seq_num=1) -> None:
        """
        Sends the file to the receiver using the Go-Back-N strategy. Uses the smallest sliding window
        of the client and receiver. Listens for ACKs and sends the next packet in the window.
        If no ACKs arrive, retransmits the window. Exits if an error is raised.
        :param self: Variables of the object itself.
        :param start_seq_num: Sequence number that the transfer should start on. Default is 1.
        """
        next_ack = start_seq_num
        last_data_packet = float("inf")      # Temp value just so it compares true with an int

        try:
            self.send_window(range(next_ack , min(next_ack + self.window_size, last_data_packet + 1)))

            #  Continue sending data packets per ACK until the last packet is ACKed.
            while True:
                try:
                    # TODO: Like this or one line?
                    packet = self.socket.recv(1000)
                    _seq_num, ack_num, flags, _window, data = parse_packet(packet)

                    if Flag.ACK == flags and ack_num == next_ack:
                        print(f"{time_now_log()} ACK for packet = {ack_num} is received")
                        next_ack += 1

                        # TODO: is it possible to simplify this?
                        if next_ack + self.window_size - 1 <= last_data_packet:
                            data = self.file_handler.get_file_data(next_ack + self.window_size - 1)
                        # Check if the last data packet has been found.
                        if last_data_packet == float('inf') and data == b"":
                            last_data_packet = next_ack + self.window_size - 2
                        # Sends data if it's not after the last data packet.
                        if next_ack + self.window_size - 1 <= last_data_packet:
                            self.socket.sendto(create_packet(next_ack + self.window_size - 1, 0, 0, 0, data), self.server_address)
                            print(f"{time_now_log()} packet with seq = {next_ack + self.window_size - 1} is sent, sliding window = {list(range(next_ack, min(next_ack + self.window_size, last_data_packet)))}")
                        if next_ack > last_data_packet: return    # Returns if the last data packet has been ACKed

                    else:
                        print(f"Received packet with wrong flag or wrong ack number received")
                except timeout:
                    print(f"{time_now_log()} RTO occurred")
                    self.send_window(range(next_ack, min(next_ack + self.window_size, last_data_packet + 1)), True)

                sleep(0.005)
        except ConnectionError:
            print("\nError: Connection refused by server while trying to send data")
            self.close_client(1)
        except OSError as e:
            print(f"\nError: {e}")
            self.close_client(1)
        self.file_handler.close_file()

    def close_connection(self) -> None:
        """
        Closes the connection by sending a FIN packet to the receiver. Then waits for a
        FIN-ACK packet to confirm closing the connection. Ignores other flags. Exits if an error is raised.
        :param self: Variables of the object itself.
        """
        # TODO: Check if closing connection work as it should both server and client
        #       What if FIN ACK isnt received.
        # TODO: what should happen if it times out?
        try:
            print("\nConnection Teardown:\n")
            # Send FIN packet
            self.socket.sendto(create_packet(0, 0, Flag.FIN, 0), self.server_address)
            print("FIN packet is sent")

            # Receive and check for FIN-ACK packet. Close if so. Ignore other flags
            while True:
                packet = self.socket.recv(1000)
                _seq_num, _ack_num, flags, _window, _data = parse_packet(packet)

                if Flag.FIN | Flag.ACK == flags:
                    print("FIN ACK packet is received\n"
                          "Connection closes")
                    break
                else:
                    print("Received packet missing FIN or ACK flag\n")
        except timeout:
            print("Timed out while waiting for FIN-ACK packet")
        except ConnectionError:
            print("\nError: Connection refused by server while trying to close connection")
            self.close_client(1)
        except OSError as e:
            print(f"\nError: {e}")
            self.close_client(1)

    # TODO: Basically the same thing in server and client
    def close_client(self, exit_code=0):
        """
        Closes the client's file handler and socket before exiting the client.
        :param self: Variables of the object itself.
        :param exit_code: The exit code that should happen when exiting.
        """
        self.file_handler.close_file()
        self.socket.close()
        print("Exiting client")
        sys.exit(exit_code)

    def run(self) -> None:
        """
        Runs the client part of the application. Establishes a connection with the server and sends
        a file with Go-Back-N strategy before closing the connection. Exits if KeyboardInterrupt is raised.
        :param self: Variables of the object itself.
        """
        try:
            self.establish_connection()

            self.send_data()

            self.close_connection()

            self.close_client()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt detected, closing client")
            self.close_client()
