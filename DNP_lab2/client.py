import socket
import sys

buff_size = 1024
numbers = [15492781, 15492787, 15492803,
           15492811, 15492810, 15492833,
           15492859, 15502547, 15520301,
           15527509, 15522343, 1550784]

if __name__ == '__main__':
    ip, port = sys.argv[1].split(':')
    address = (ip, int(port))

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(address)
        print(f'Connected to {address}')
        for n in numbers:
            client_socket.send(str(n).encode())
            data = client_socket.recv(buff_size).decode()
            print(f'{n} is {data}')
        print('Completed')
    except ConnectionError as e:
        client_socket.close()
    finally:
        client_socket.close()
