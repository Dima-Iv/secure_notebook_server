import socket
import os
import string
from random import random

import rsa

dir_for_clients_files = 'clients_files/'
host = 'localhost'
port = 8007
count_of_clients = 10
max_len_of_data = 1000000
key_len = 10
dict_for_login_and_pass = {}
dict_for_login_and_session_key = {}


def get_login_and_password(connection):
    connection.send('Enter login and password:'.encode())
    return connection.recv(max_len_of_data).decode().strip().split()


def open_file(connection, finish_path_to_file, action):
    if action == 'create file':
        with open(finish_path_to_file, 'w') as f:
            connection.send('Enter info'.encode())
            data = connection.recv(max_len_of_data).decode()
            f.write(data + '\n')
    else:
        with open(finish_path_to_file, 'r') as f:
            connection.send(f.read().encode())
            connection.recv(max_len_of_data)
        with open(finish_path_to_file, 'a') as fil:
            connection.send('Enter info:'.encode())
            data = connection.recv(max_len_of_data).decode()
            fil.write(data + '\n')
    connection.send('Successful'.encode())


def registration(connection):
    while True:
        current_login, current_passw = get_login_and_password(connection)
        if dict_for_login_and_pass.get(current_login, None) is not None:
            conn.send('This login is occupied'.encode())
        else:
            dict_for_login_and_pass[current_login] = current_passw
            os.mkdir(dir_for_clients_files + current_login)
            with open(dir_for_clients_files + 'users_passwords.txt', 'a') as f:
                f.write(current_login + '\t' + current_passw + '\n')
            break


def login(connection):
    while True:
        log, passw = get_login_and_password(connection)
        current_passw = dict_for_login_and_pass.get(log, None)
        if current_passw is None:
            connection.send('This login is not exist'.encode())
        elif current_passw == passw:
            break
    while True:
        connection.send('Choose action:\ngen session key\ncreate file\nupdate file\ndelete file\nexit\n'.encode())
        action = connection.recv(max_len_of_data).lower().decode()
        if action == 'exit':
            break
        elif operation == 'gen session key':
            get_session_key(log)
            connection.send('Enter open RSA key\n'.encode())
            open_RSA_key = connection.recv(max_len_of_data).decode()
            encrypted_session_key = rsa.encrypt(dict_for_login_and_session_key[log], open_RSA_key)
            connection.send(str(encrypted_session_key).encode())
            connection.recv(max_len_of_data)
        else:
            connection.send('Enter file name\n'.encode())
            file_name = connection.recv(max_len_of_data).decode()
            finish_path_to_file = dir_for_clients_files + log + '/' + file_name + '.txt'
            if action == 'create file' or action == 'update file':
                open_file(connection, finish_path_to_file, action)
            elif action == 'delete file':
                os.remove(finish_path_to_file)


def get_session_key(user_log, pool: str = string.ascii_letters):
    session_key = ''.join(random.choices(pool, k=key_len))
    dict_for_login_and_session_key[user_log] = session_key


with open(dir_for_clients_files + 'users_passwords.txt') as file:
    for line in file:
        log, passw = line.strip().split()
        dict_for_login_and_pass[log] = passw
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(count_of_clients)
conn, address = s.accept()
while True:
    conn.send('Choose operation:\nregistration\nlogin\nexit'.encode())
    operation = conn.recv(max_len_of_data).lower().decode()
    if operation == 'registration':
        registration(conn)
    elif operation == 'login':
        login(conn)
    elif operation == 'exit':
        break
