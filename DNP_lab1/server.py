import socket
import sys
import time

local_ip = '127.0.0.1'
buff_size = 1024
split_char = " | ".encode()
accepted_data = {}


def write_to_file(address):
    filename = accepted_data[address]['filename']
    with open(filename, 'wb') as binary_file:
        binary_file.write(accepted_data[address]['data'])
        print(f'Data from {address} is written to {filename}')
        del accepted_data[address]


def start_connection(address, accepted_seqno, filename, total_size):
    accepted_data[address] = {
        'last_seqno': accepted_seqno,
        'filename': filename.decode(),
        'total_size': int(total_size.decode()),
        'data': b'',
        'timestamp': time.time()
    }


def add_data(address, accepted_seqno, data_bytes):
    if accepted_seqno == accepted_data[address]['last_seqno']:
        return
    accepted_data[address]['last_seqno'] = accepted_seqno
    accepted_data[address]['timestamp'] += time.time()
    accepted_data[address]['data'] += data_bytes


def recognize_message(message, address):
    split_msg = message.split(split_char)
    msg_type, seqno = split_msg[0], int(split_msg[1].decode())

    response = ''
    if msg_type == b's':
        start_connection(address, seqno, split_msg[2], split_msg[3])
        response += f' | {buff_size}'
    elif msg_type == b'd':
        add_data(address, seqno, split_msg[2])

    next_seqno = accepted_data[address]['last_seqno']
    response = f'a | {next_seqno + 1}' + response
    if len(accepted_data[address]['data']) == accepted_data[address]['total_size']:
        write_to_file(address)
    return response.encode()


if __name__ == '__main__':
    port = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((local_ip, port))
    server_socket.settimeout(0.1)

    while True:
        try:
            msg, client_address = server_socket.recvfrom(buff_size)
            response_msg = recognize_message(msg, client_address)
            server_socket.sendto(response_msg, client_address)
        except KeyboardInterrupt:
            break
        except Exception:
            time_now = time.time()
            to_del = []
            for key in accepted_data:
                if time_now - accepted_data[key]['timestamp'] > 3:
                    to_del.append(key)
            for key in to_del:
                del accepted_data[key]
    print('\nServer closed')
    server_socket.close()
