import sys
import grpc
import Service_pb2 as pb2
import Service_pb2_grpc as pb2_grpc
from concurrent import futures
from math import sqrt


def is_prime(n):
    for i in range(2, int(sqrt(n)) + 1):
        if (n % i) == 0:
            return f'{n} is not prime'
    return f'{n} is prime'


class ServiceHandler(pb2_grpc.ServiceServicer):
    def reverse(self, request, context):
        text = request.text
        reply = {"message": text[::-1]}
        return pb2.ReverseMessageResponse(**reply)

    def split(self, request, context):
        text, delim = request.text, request.delim
        text_array = text.split(delim)
        reply = {
            "number": len(text_array),
            "parts": text_array
        }
        return pb2.SplitMessageResponse(**reply)

    def isprime(self, request_iterator, context):
        for msg in request_iterator:
            reply = {"text": is_prime(msg.number)}
            yield pb2.IsPrimeMessageResponse(**reply)


if __name__ == '__main__':
    port = sys.argv[1]

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ServiceServicer_to_server(ServiceHandler(), server)

    server.add_insecure_port(f'127.0.0.1:{port}')
    server.start()
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print('Shutting down')
