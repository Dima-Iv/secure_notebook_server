import socket

from src.client_info import ClientInfo
from src.runner import Runner

DIR_FOR_CLIENTS_FILES = 'clients_files/'
HOST = ''
PORT = 8007
COUNT_OF_CLIENTS = 10
DICT_FOR_LOGIN_AND_PASS = {}


def get_server_socket():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(COUNT_OF_CLIENTS)
    return server


with open(DIR_FOR_CLIENTS_FILES + 'users_passwords.txt', 'r') as file:
    for line in file:
        login, password = line.strip().split()
        DICT_FOR_LOGIN_AND_PASS[login] = password
ClientInfo.dict_for_login_and_pass = DICT_FOR_LOGIN_AND_PASS
server_socket = get_server_socket()
while True:
    conn, address = server_socket.accept()
    conn.send('accepted'.encode())
    print('server start')
    Runner(ClientInfo(conn, address)).start()
