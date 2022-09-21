import sys
import grpc
import Service_pb2 as pb2
import Service_pb2_grpc as pb2_grpc


def make_message(number):
    return pb2.IsPrimeMessage(
        number=number
    )


def generate_messages(numbers):
    messages = []
    numbers = map(int, numbers.split())
    for num in numbers:
        messages.append(make_message(num))
    for msg in messages:
        yield msg


if __name__ == '__main__':
    host = sys.argv[1]

    channel = grpc.insecure_channel(host)
    stub = pb2_grpc.ServiceStub(channel)

    while True:
        line = input('> ')

        if line == 'exit':
            print('Shutting down')
            break

        arr = line.split(' ', 1)
        cmd, args = arr[0], arr[1]

        if cmd == 'reverse':
            msg = pb2.ReverseMessage(text=args)
            response = stub.reverse(msg)
            print(response)
        elif cmd == 'split':
            msg = pb2.SplitMessage(text=args, delim=' ')
            response = stub.split(msg)
            print(response)
        elif cmd == 'isprime':
            responses = stub.isprime(generate_messages(args))
            for response in responses:
                print(response.text)
        else:
            print('Unacceptable command')



