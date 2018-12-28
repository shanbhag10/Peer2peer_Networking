import socket
import os
import sys
import pickle
import random

if len(sys.argv) != 4:
    print("Incorrect format!")
    print("Correct Format - python simple_ftp_server.py server-port recv-file-name packet-loss-probability")
    exit(0)

# Get all the parameters from command line.
# Port number
server_port = int(sys.argv[1])
# File name
recv_file_name = sys.argv[2]
# Probability of packet loss
prob_packet_loss = float(sys.argv[3])

last_recv_packet = -1

# Acknowledgement type
ack_type = "1010101010101010"
# End of file type
EOF_type = "1111111111111111"
# Data type
data_type = "0101010101010101"
# Padding
data_padding = "0000000000000000"

ack_port = 7735
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ack_host = ""

host = '0.0.0.0'
server_socket.bind((host, server_port))

# Removing file if already present
if os.path.isfile(recv_file_name):
    os.remove(recv_file_name)

# TODO: Remove
# def writing_File(packet_data):
#     with open(recv_file_name, 'ab') as x:
#         x.write(packet_data)


# Function to send acknowledgements with the given acknowledgement number.
def send_ack(ack_no):
    ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_packet = pickle.dumps([ack_no, data_padding, ack_type])
    ack_sock.sendto(ack_packet, (ack_host, ack_port))
    ack_sock.close()


# TODO: Remove
# def randNum():
#     return random.random()


# TODO: Remove
# def carry_add(a, b):
#     c = a + b
#     return (c & 0xFFFF) + (c >> 16)


# Function to check if the packet should be dropped (using the probability of packet loss obtained from command line)
# TODO: Remove
# def is_packet_dropped(prob_packet_loss, packet_seq_no):
def is_packet_dropped():
    if prob_packet_loss >= random.random():
        return True
    return False


# TODO: Remove
# def checksum(data):
#     if (len(data) % 2) != 0:
#         data += "0"
#     temp = 0
#     for idx in range(0, len(data), 2):
#         t = ord(data[idx]) + (ord(data[idx + 1]) << 8)
#         res = temp + t
#         temp = (res & 0xFFFF) + (res >> 16)
#         # TODO: Remove
#         # s = carry_add(s, w)
#     return ~temp & 0xFFFF


# TODO: Remove
# def validate_checksum(blob, checksum_check):
#     if calculate_checksum(blob, checksum_check) == 0:
#         return True
#     return False


# Method for checksum computation
def calculate_checksum(blob, checksum_check):
    blob_length = len(blob)
    byte = 0
    while byte < blob_length:
        # Convert into unicode representation
        byte1 = ord(blob[byte])
        byte1_shift = byte1 << 8
        byte2 = 0xffff
        if byte + 1 != blob_length:
            byte2 = ord(blob[byte + 1])

        bytes_combined = byte1_shift + byte2
        checksum_add = checksum_check + bytes_combined
        main_checksum = checksum_add & 0xffff
        carry = checksum_add >> 16
        checksum_check = carry + main_checksum
        byte += 2
    return checksum_check ^ 0xffff


def main():
    global last_recv_packet, ack_host
    not_complete = True
    while not_complete:
        recv_data_temp, address = server_socket.recvfrom(65535)
        ack_host = address[0]
        recv_data = pickle.loads(recv_data_temp)
        packet_seq_no, packet_checksum, packet_type, packet_data = recv_data[0], recv_data[1], recv_data[2], recv_data[3]

        if packet_type == data_type:
            # TODO: Remove
            # drop_packet = is_packet_dropped(prob_packet_loss, packet_seq_no)
            # TODO: Remove
            # if not drop_packet:
            # if not is_packet_dropped(prob_packet_loss, packet_seq_no):
            if not is_packet_dropped():
                # TODO: Remove
                # if validate_checksum(packet_data, packet_checksum):
                if calculate_checksum(packet_data, packet_checksum) == 0:
                    if packet_seq_no == last_recv_packet + 1:
                        send_ack(packet_seq_no + 1)
                        last_recv_packet += 1
                        # Write the contents to the new file.
                        with open(recv_file_name, 'ab') as fp:
                            fp.write(packet_data)
                        # TODO: Remove
                        # writing_File(packet_data)
                    else:
                        send_ack(last_recv_packet + 1)
                else:
                    print("Packet {0} dropped. Reason - Incorrect checksum".format(str(packet_seq_no)))
            else:
                print("Packet loss, sequence number = {0}".format(str(packet_seq_no)))
        elif packet_type == EOF_type:
            not_complete = False
            server_socket.close()


if __name__ == "__main__":
    main()
