import zmq
import sys
import time

host = '127.0.0.1'

if __name__ == '__main__':
    ci_port, co_port = sys.argv[1:]

    context = zmq.Context()

    client_inputs_sock = context.socket(zmq.REP)
    client_outputs_sock = context.socket(zmq.PUB)

    client_inputs_sock.bind(f'tcp://{host}:{ci_port}')
    client_outputs_sock.bind(f'tcp://{host}:{co_port}')

    client_inputs_sock.RCVTIMEO = 10

    summary = []
    timer = time.time()

    try:
        while True:
            try:
                message = client_inputs_sock.recv_string()
                summary.append(message)
                client_inputs_sock.send_string('ok')
            except zmq.Again:
                pass
            except Exception as e:
                print(e)

            # Send after 5 seconds
            if time.time() - timer >= 5:
                message = 'SUMMARY'
                for msg in summary:
                    message += f'\n  {msg}'

                client_outputs_sock.send_string(message)
                summary = []
                timer = time.time()

    except KeyboardInterrupt:
        print("Terminating server")
        client_inputs_sock.close()
        client_outputs_sock.close()
        sys.exit(0)
