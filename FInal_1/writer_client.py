import zmq
import sys

host = '127.0.0.1'

if __name__ == '__main__':
    ci_port, name = sys.argv[1:]

    context = zmq.Context()

    client_inputs_sock = context.socket(zmq.REQ)

    client_inputs_sock.connect(f'tcp://{host}:{ci_port}')

    try:
        while True:
            line = input("> ")
            if len(line) != 0:
                to_send = name + ': ' + line
                client_inputs_sock.send_string(to_send)
                confirmation = client_inputs_sock.recv_string()
            else:
                print('PLEASE WrITE NON EMPTY STRING')
    except KeyboardInterrupt:
        print("Terminating client")
        client_inputs_sock.close()
        sys.exit(0)
