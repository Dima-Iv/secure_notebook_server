import socket

host = 'localhost'
port = 8007
max_len_of_data = 1000000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
while True:
    request = s.recv(max_len_of_data)
    print(request.decode())
    response = input()
    if response == 'exit':
        break
    s.send(response.encode())
s.close()
