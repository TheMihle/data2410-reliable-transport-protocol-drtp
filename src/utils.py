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
    in binary mode. The File stays open until closed.

    Has methods for reading from a file based on segment number and size and
    for writing to the end of a file.
    """
    def __init__(self, file_name: str, segment_size: int = 1000):
        """
        Initialises the FileHandler with the specified file name and segment size.

        FileHandler handles file operations, for example, opening, reading, writing and closing
        in binary mode. The File stays open until closed.
        :param file_name: Filename of the file to be read from or written to.
        :param segment_size: Size of the segments to be read in bytes.
               Does nothing for writing. (default 1000 bytes)
        """
        self.file_name = file_name
        self.file = None
        self.segment_size = segment_size

    def get_file_data(self, segment_num: int) -> bytes:
        """
        Gets the file data with a specified size and number.
        Recommended to stick with one segment size.
        :param segment_num: Segment number of the data to be read
        :raises UnsupportedOperation: If switching between reading and writing
                data without closing first.
        """
        position: int = (segment_num - 1) * self.segment_size

        if self.file is None:
            self.file = open(self.file_name, "rb")

        self.file.seek(position)
        return self.file.read(self.segment_size)

    def write_to_file(self, data) -> None:
        """
        Writes to the end of the file.
        :param data: Written to the end of the file.
        :raises UnsupportedOperation: If switching between reading and writing
                data without closing first.
        """
        if self.file is None:
            self.file = open(self.file_name, "ab")

        self.file.write(data)

    def close_file(self) -> None:
        """
        Closes and clears the file from the object.
        """
        if self.file is not None:
            self.file.close()
            self.file = None


def create_packet(seq_num: int, ack_num: int, flags: int, window: int, data: bytes = None) -> bytes:
    """
    Creates a packet based on the input parameters.
    :param seq_num: Seq number of the packet
    :param ack_num: Seq number of the packet that should be ACKed
    :param flags: The flags the packet should have, e.g. Flag.ACK | Flag.SYN
    :param window: Receiver window size
    :param data: The data that should be sent in the packet, if not provided,
                the packet will be empty. Must be in bytes.
    """
    header_format: str = "!HHHH"
    packet = pack(header_format, seq_num, ack_num, flags, window)

    if data is not None:
        packet += data
    return packet


def parse_packet(packet: bytes) -> tuple[int, int, int, int, bytes]:
    """
    Parses the packet and returns the header information and data
    :param packet: The packet that should be parsed
    :return: Tuple with seq_num, ack_num, flags, window, data
    """
    header_format: str = "!HHHH"
    header_size: int = calcsize(header_format)
    data: bytes = packet[header_size:]
    header_data: tuple = unpack(header_format, packet[:header_size])
    return *header_data, data


def time_now_log() -> str:
    """
    Creates a string with current time formatted as "HH:MM:SS.mmmmmm --"
    ready to specify time in a log.
    :return: Current time formatted in a string.
    """
    return f"{datetime.now().strftime("%H:%M:%S.%f")} --"
