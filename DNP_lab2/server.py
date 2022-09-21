import socket
import sys
from threading import Thread
from multiprocessing import Queue

workers_count = 2
local_ip = '127.0.0.1'
server_stopped = False
buff_size = 1024


def is_prime(n):
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for divisor in range(3, n, 2):
        if n % divisor == 0:
            return False
    return True


def worker(queue: Queue):
    global server_stopped
    is_free = True
    connection, address = None, None

    while True:
        if is_free and not queue.empty():
            connection, address = queue.get()
            print(f'{address} connected')
            is_free = False

        if not is_free:
            data = connection.recv(buff_size).decode()
            if not data:
                is_free = True
                connection.close()
                print(f'{address} disconnected')
                continue
            num = int(data)
            answer = 'prime' if is_prime(num) else 'not prime'
            connection.send(answer.encode())

        if server_stopped:
            try:
                connection.close()
            finally:
                break


if __name__ == '__main__':
    port = int(sys.argv[1])
    connections_queue = Queue()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((local_ip, port))
    server_socket.listen(5)

    threads = [Thread(target=worker, args=(connections_queue,)),
               Thread(target=worker, args=(connections_queue,))]
    [t.start() for t in threads]

    try:
        while True:
            conn, addr = server_socket.accept()
            connections_queue.put((conn, addr))
    except KeyboardInterrupt:
        print('\nShutting down')
        server_stopped = True
        [t.join() for t in threads]
        server_socket.close()
        print('Done')
