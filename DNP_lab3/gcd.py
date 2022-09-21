import zmq
import sys
from math import gcd

host = '127.0.0.1'


def gcd_value(a, b):
    return f'gcd for {a} {b} is {gcd(a, b)}'


if __name__ == '__main__':
    wi_port, wo_port = sys.argv[1:]

    context = zmq.Context()

    worker_inputs_sock = context.socket(zmq.SUB)
    worker_outputs_sock = context.socket(zmq.PUB)

    worker_inputs_sock.connect(f'tcp://{host}:{wi_port}')
    worker_outputs_sock.connect(f'tcp://{host}:{wo_port}')

    worker_inputs_sock.setsockopt_string(zmq.SUBSCRIBE, 'gcd')
    worker_inputs_sock.RCVTIMEO = 100

    try:
        while True:
            try:
                message = worker_inputs_sock.recv_string()
                a, b = map(int, message.split()[1:])
                worker_outputs_sock.send_string(gcd_value(a, b))
            except zmq.Again:
                pass
            except Exception as e:
                print(e)
    except KeyboardInterrupt:
        print("Terminating GCD server")
        worker_inputs_sock.close()
        worker_outputs_sock.close()
        sys.exit(0)
