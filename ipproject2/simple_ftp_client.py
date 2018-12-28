# TODO: Remove
# from collections import namedtuple

from multiprocessing import Lock
import signal
import pickle
import time
import threading
import sys
import socket
import collections


if len(sys.argv) != 6:
    print("Incorrect format!")
    print("Correct Format - python simple_ftp_client.py server-IP server-port-no send-file-name N-value MSS-value")
    exit(0)

# Get all the parameters from command line.
# Host IP address
send_host = sys.argv[1]
# Port number
send_port = int(sys.argv[2])
# File name
send_file_name = sys.argv[3]
# N VALUE
N = int(sys.argv[4])
# MSS VALUE
MSS = int(sys.argv[5])

# Defining remaining global variables.
last_ack_packet = -1
max_sequence_no = 0
last_send_packet = -1

start_time = 0
end_time = 0
total_time = 0

# Retransmission timeout
RTT = 0.1
# Acknowledgement type
ack_type = "1010101010101010"
# Data type
data_type = "0101010101010101"
# End of file type
EOF_type = "1111111111111111"

ack_port = 7735
ack_host = '0.0.0.0'

sliding_window = set()
buffer = collections.OrderedDict()
# Flag to find if sending is done.
finish_send = False

# TODO: Remove these.
# data_packet = namedtuple('data_packet', 'sequence_no checksum type data')
# ack_packet = namedtuple('ack_packet', 'sequence_no padding type')

thread_lock = Lock()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# TODO: Remove
# function to send packet
# def send_packet(packet, host, port, socket, sequence_no):
#     sock.sendto(packet, (send_host, send_port))

# TODO: Remove
# def carry_add(a, b):
#     c = a + b
#     return (c & 0xFFFF) + (c >> 16)


# rdt_send method
# TODO: Remove
# def rdt_send(sock, file_content, host, port):
def rdt_send():
    global last_send_packet, last_ack_packet, sliding_window, buffer, start_time
    start_time = time.time()
    while len(sliding_window) < min(len(buffer), N):
        if last_ack_packet == -1:
            sock.sendto(buffer[last_send_packet + 1], (send_host, send_port))
            # send_packet(buffer[1 + last_send_packet], host, port, sock, 1 + last_send_packet)
            signal.alarm(0)
            signal.setitimer(signal.ITIMER_REAL, RTT)
            last_send_packet += 1
            sliding_window.add(last_send_packet)
            temp = 0
            while temp < 100000:
                temp = temp + 1


# method for checksum computation
def checksum_compute(segment):
    temp_checksum = 0
    segment = str(segment)
    b_length = len(segment)
    byte = 0
    while byte < b_length:
        # Converting into unicode representation
        byte1 = ord(segment[byte])
        byte1_shift = byte1 << 8
        if 1 + byte != b_length:
            byte2 = ord(segment[byte + 1])
        else:
            byte2 = 0xffff
        bytes_merged = byte1_shift + byte2
        checksum_add = temp_checksum + bytes_merged
        main_part = checksum_add & 0xffff
        # TODO: Remove
        # cry = checksum_add >> 16
        temp_checksum = (checksum_add >> 16) + main_part
        byte += 2

    # returning 1's complement
    return temp_checksum ^ 0xffff


# TODO: Remove
# def checksum(data):
#     if (len(data) % 2) != 0:
#         data += "0"
#     s = 0
#     for i in range(0, len(data), 2):
#         w = ord(data[i]) + (ord(data[i + 1]) << 8)
#
#         # s = carry_add(s, w)
#
#         temp = s + w
#         s = temp & 0xFFFF + temp >> 16
#     return ~s & 0xFFFF


# Monitor the incoming ACKs and send the remaining packets
def ack_process():
    global last_ack_packet, last_send_packet, buffer, sliding_window, sock, send_port, send_host, finish_send, end_time, start_time, total_time

    ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ack_sock.bind((ack_host, ack_port))
    while True:
        reply = pickle.loads(ack_sock.recv(65535))

        if reply[2] == ack_type:
            curr_ack_sequence_no = reply[0] - 1
            if last_ack_packet + 1 >= 0:
                thread_lock.acquire()
            if max_sequence_no == curr_ack_sequence_no:
                eof_packet = pickle.dumps(["0", "0", EOF_type, "0"])
                sock.sendto(eof_packet, (send_host, send_port))
                # TODO: Remove
                # thread_lock.release()
                finish_send = True
                end_time = time.time()
                total_time = end_time - start_time
                break
            elif curr_ack_sequence_no > last_ack_packet:
                while curr_ack_sequence_no > last_ack_packet:
                    signal.alarm(0)
                    signal.setitimer(signal.ITIMER_REAL, RTT)
                    last_ack_packet += 1
                    sliding_window.remove(last_ack_packet)
                    buffer.pop(last_ack_packet)

                    while min(len(buffer), N) > len(sliding_window):
                        if max_sequence_no > last_send_packet:
                            sock.sendto(buffer[1 + last_send_packet], (send_host, send_port))
                            # TODO: Remove
                            # send_packet(buffer[1 + last_send_packet], send_host, send_port, sock, 1 + last_send_packet)
                            sliding_window.add(1 + last_send_packet)
                            last_send_packet += 1

        # TODO: Remove
        #     thread_lock.release()
        # else:
        #     thread_lock.release()
        thread_lock.release()


# method for timeout of thread, locking and unlocking threads
def timeout_thread(timeout_thr, frame):
    global last_ack_packet
    if last_send_packet == last_ack_packet + len(sliding_window):
        print("Timeout, sequence num = " + str(last_ack_packet + 1))
        thread_lock.acquire()
        for i in range(last_ack_packet + 1, last_ack_packet + len(sliding_window) + 1):
            signal.alarm(0)
            signal.setitimer(signal.ITIMER_REAL, RTT)
            sock.sendto(buffer[i], (send_host, send_port))
            # TODO: Remove
            # send_packet(buffer[i], send_host, send_port, sock, i)

        thread_lock.release()


def main():
    global buffer, max_sequence_no, sock, send_port, send_host, MSS

    sequence_no = 0
    try:
        with open(send_file_name, 'rb') as x:
            while True:
                segment = x.read(MSS)
                if segment:
                    max_sequence_no = sequence_no
                    segment_checksum = checksum_compute(segment)
                    buffer[sequence_no] = pickle.dumps([sequence_no, segment_checksum, data_type, segment])
                    sequence_no += 1
                else:
                    break
    except:
        sys.exit("Couldn't open the file - " + send_file_name)

    signal.signal(signal.SIGALRM, timeout_thread)
    # creating thread
    ack_thread = threading.Thread(target=ack_process)
    ack_thread.start()

    # TODO: Remove
    # rdt_send(sock, buffer, send_host, send_port)

    # Send data.
    rdt_send()

    while True:
        if finish_send:
            break

    ack_thread.join()
    sock.close()


if __name__ == "__main__":
    main()
