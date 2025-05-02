from enum import IntFlag
from struct import pack, unpack


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


def create_packet(seq_num, ack_num, flags, window, data=None):
    """

    :param seq_num: Seq number of the packet
    :param ack_num: Seq number of the packet that should be ACKed
    :param flags: The flags the packet should have, e.g. Flag.ACK | Flag.SYN
    :param window:
    :param data: The data that should be sent in the packet, if not provided,
                the packet will be empty. Must be in bytes.
    """
    header_format = "!HHHH"

    header = pack(header_format, seq_num, ack_num, flags, window)
    packet2 = header
    return packet2


def read_packet(packet) -> tuple:
    """

    :param packet: the packet that should be parsed
    :return: tuple with seq_num, ack_num, flags, window
    """
    header_format = "!HHHH"
    packet = unpack(header_format, packet[:8])  # Reads only the header
    return packet[0], packet[1], packet[2], packet[3]
