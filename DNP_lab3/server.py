import zmq
import sys

host = '127.0.0.1'

if __name__ == '__main__':
    ci_port, co_port, wi_port, wo_port = sys.argv[1:]

    context = zmq.Context()

    client_inputs_sock = context.socket(zmq.REP)
    client_outputs_sock = context.socket(zmq.PUB)
    worker_inputs_sock = context.socket(zmq.PUB)
    worker_outputs_sock = context.socket(zmq.SUB)

    client_inputs_sock.bind(f'tcp://{host}:{ci_port}')
    client_outputs_sock.bind(f'tcp://{host}:{co_port}')
    worker_inputs_sock.bind(f'tcp://{host}:{wi_port}')
    worker_outputs_sock.bind(f'tcp://{host}:{wo_port}')

    worker_outputs_sock.setsockopt_string(zmq.SUBSCRIBE, '')

    client_inputs_sock.RCVTIMEO = 100
    worker_outputs_sock.RCVTIMEO = 100

    try:
        while True:
            try:
                message = client_inputs_sock.recv_string()
                client_inputs_sock.send_string('ok')
                client_outputs_sock.send_string(message)
                worker_inputs_sock.send_string(message)
            except zmq.Again:
                pass
            except Exception as e:
                print(e)

            try:
                message = worker_outputs_sock.recv_string()
                client_outputs_sock.send_string(message)
            except zmq.Again:
                pass
            except Exception as e:
                print(e)
    except KeyboardInterrupt:
        print("Terminating server")
        client_inputs_sock.close()
        client_outputs_sock.close()
        worker_inputs_sock.close()
        worker_outputs_sock.close()
        sys.exit(0)
