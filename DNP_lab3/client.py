import zmq
import sys

host = '127.0.0.1'

if __name__ == '__main__':
    ci_port, co_port = sys.argv[1:]

    context = zmq.Context()

    client_inputs_sock = context.socket(zmq.REQ)
    client_outputs_sock = context.socket(zmq.SUB)

    client_inputs_sock.connect(f'tcp://{host}:{ci_port}')
    client_outputs_sock.connect(f'tcp://{host}:{co_port}')

    client_outputs_sock.setsockopt_string(zmq.SUBSCRIBE, '')
    client_outputs_sock.RCVTIMEO = 100

    try:
        while True:
            line = input("> ")
            if len(line) != 0:
                client_inputs_sock.send_string(line)
                confirmation = client_inputs_sock.recv_string()
            try:
                while True:
                    message = client_outputs_sock.recv_string()
                    print(message)
            except zmq.Again:
                pass
    except KeyboardInterrupt:
        print("Terminating client")
        client_inputs_sock.close()
        client_outputs_sock.close()
        sys.exit(0)
