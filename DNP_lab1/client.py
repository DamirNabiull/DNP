import socket
import sys
import math
import os

data_to_transfer = b''
split_char = " | ".encode()
buff_size = 1024
prefix_size = 12
seqno = 0
total_size = 0
chunk_size = 0
chunks_count = 0


def start_message(filename):
    global total_size, seqno
    return f's | {seqno} | {filename} | {total_size}'.encode()


def data_message():
    global seqno, data_to_transfer
    ind = (seqno - 1) * chunk_size
    return f'd | {seqno} | '.encode() + data_to_transfer[ind:ind+chunk_size]


def read_file(file_path):
    global data_to_transfer, total_size
    with open(file_path, 'rb') as file:
        data_to_transfer = file.read()
    total_size = len(data_to_transfer)


def recognize_message(message):
    global chunk_size, chunks_count, total_size, seqno
    split_msg = message.split(split_char)
    msg_type, next_seqno = split_msg[0], int(split_msg[1].decode())
    if msg_type != b'a':
        raise TypeError
    seqno = next_seqno
    if len(split_msg) == 3:
        buf_size = int(split_msg[2].decode())
        chunk_size = buf_size - prefix_size
        chunks_count = math.ceil(total_size / chunk_size)
        print(f'bufsize selected by server: {buf_size}')


if __name__ == '__main__':
    address, local_path, remote_name = sys.argv[1:]
    address = address.split(':')
    address = (address[0], int(address[1]))
    read_file(local_path)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(2)

    tries = 0
    state = 0
    while True:
        if state == 0:
            try:
                client_socket.sendto(start_message(remote_name), address)
                msg, _ = client_socket.recvfrom(buff_size)
                recognize_message(msg)
                tries = 0
                state = 1
            except Exception:
                tries += 1
                if tries > 5:
                    print('Failed to get ack for start message')
                    client_socket.close()
                    break
                print(f'seqNo={seqno} retry')
                continue

        if state == 1:
            try:
                if seqno > chunks_count:
                    print('Successfully transmitted a file')
                    client_socket.close()
                    break
                client_socket.sendto(data_message(), address)
                msg, _ = client_socket.recvfrom(buff_size)
                recognize_message(msg)
            except Exception:
                print(f'seqNo={seqno} failed to send data')
                print(f'seqNo={seqno} retry')
                continue
