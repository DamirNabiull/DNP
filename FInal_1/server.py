import zmq
import sys
import time

host = '127.0.0.1'
INTERVAL_DURATION = 5

if __name__ == '__main__':
    ci_port, co_port = sys.argv[1:]

    context = zmq.Context()

    client_inputs_sock = context.socket(zmq.REP)
    client_outputs_sock = context.socket(zmq.PUB)

    client_inputs_sock.bind(f'tcp://{host}:{ci_port}')
    client_outputs_sock.bind(f'tcp://{host}:{co_port}')

    client_inputs_sock.RCVTIMEO = 10

    summary = {}
    timer = time.time()

    try:
        while True:
            try:
                message = client_inputs_sock.recv_string()

                name, msg = message.split(': ')
                if name in summary:
                    summary[name] += 1
                else:
                    summary[name] = 1

                client_inputs_sock.send_string('ok')
                client_outputs_sock.send_string(message)
            except zmq.Again:
                pass
            except Exception as e:
                print(e)

            # Send after 5 seconds
            if time.time() - timer >= INTERVAL_DURATION:
                message = 'SUMMARY'
                keys = list(summary.keys())
                keys.sort()
                for name in keys:
                    message += f'\n  {name}: {summary[name]}'
                    summary[name] = 0

                client_outputs_sock.send_string(message)
                timer = time.time()

    except KeyboardInterrupt:
        print("Terminating server")
        client_inputs_sock.close()
        client_outputs_sock.close()
        sys.exit(0)
