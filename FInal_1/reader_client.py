import zmq
import sys

host = '127.0.0.1'

if __name__ == '__main__':
    co_port = sys.argv[1]

    context = zmq.Context()

    client_outputs_sock = context.socket(zmq.SUB)

    client_outputs_sock.connect(f'tcp://{host}:{co_port}')

    client_outputs_sock.setsockopt_string(zmq.SUBSCRIBE, '')
    client_outputs_sock.RCVTIMEO = 10

    try:
        while True:
            try:
                message = client_outputs_sock.recv_string()
                print(message)
            except zmq.Again:
                pass
    except KeyboardInterrupt:
        print("Terminating client")
        client_outputs_sock.close()
        sys.exit(0)
