from datetime import datetime
from enum import IntFlag
from struct import pack, unpack, calcsize


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


class FileHandler:
    """
    Handles file operations, for example, opening, reading, writing and closing
    in binary mode. File stays open until closed.

    Has methods for reading from a file based on segment number and size and
    for writing to the end of a file.
    """
    def __init__(self, file_name):
        self.file_name = file_name
        self.file = None

    def get_file_data(self, segment_num, segment_size):
        """
        Gets the file data with a specified size and number.
        Recommended to stick with one segment size.
        :param segment_num: Segment number of the data to be read
        :param segment_size: Size of the segment to be read in bytes
        :raises UnsupportedOperation: If switching between reading and writing
                data without closing first.
        """
        position = (segment_num - 1) * segment_size

        if self.file is None:
            self.file = open(self.file_name, "rb")

        self.file.seek(position)
        return self.file.read()

    def write_to_file(self, data):
        """
        Writes to the end of the file
        :param data: Written to the end of the file
        """
        if self.file is None:
            self.file = open(self.file_name, "ab")

        self.file.write(data)

    def close_file(self):
        """
        Closes and clears the file from the object.
        """
        if self.file is not None:
            self.file.close()
            self.file = None


def create_packet(seq_num, ack_num, flags, window, data=None):
    """
    Creates a packet based on the input parameters
    :param seq_num: Seq number of the packet
    :param ack_num: Seq number of the packet that should be ACKed
    :param flags: The flags the packet should have, e.g. Flag.ACK | Flag.SYN
    :param window: Receiver window size
    :param data: The data that should be sent in the packet, if not provided,
                the packet will be empty. Must be in bytes.
    """
    header_format = "!HHHH"

    packet = pack(header_format, seq_num, ack_num, flags, window)

    if data is not None:
        packet += data
    return packet


def parse_packet(packet) -> tuple:
    """
    Parses the packet and returns the header information and data
    :param packet: The packet that should be parsed
    :return: Tuple with seq_num, ack_num, flags, window, data
    """
    header_format = "!HHHH"
    header_size = calcsize(header_format)
    data = packet[header_size:]
    packet = unpack(header_format, packet[:header_size])
    return *packet, data


def time_now_log():
    """
    Creates a string with current time formatted as "HH:MM:SS.mmmmmm --"
    ready to specify time in a log.
    :return: Current time formatted in a string.
    """
    return f"{datetime.now().strftime("%H:%M:%S.%f")} --"
