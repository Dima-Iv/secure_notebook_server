import os
import time
from socket import socket

import rsa


class ClientInfo:
    dict_for_login_and_pass = None
    KEY_LEN = 1024
    PATH_TO_LOGIN_PASSWORD = 'clients_files/users_passwords.txt'

    def __init__(self, connection: socket, address):
        self.connection = connection
        self.address = address
        self.login = ''
        self.password = ''
        self.client_public_RSA_key = None
        self.server_keys_chain = None
        self.key_time = 0

    @property
    def final_path_to_dir(self):
        return 'clients_files/' + self.login

    @staticmethod
    def decrypt(msg: bytes, serv_private_key):
        ans = b''
        m = ClientInfo.KEY_LEN // 8
        n = len(msg) // m
        for i in range(n):
            ans += rsa.decrypt(msg[i * m:(i + 1) * m], serv_private_key)
        return ans

    @staticmethod
    def encrypt(msg: bytes, client_public_key):
        ans = b''
        m = (ClientInfo.KEY_LEN // 8) - 11
        n = len(msg) // m
        for i in range(n):
            ans += rsa.encrypt(msg[i * m:(i + 1) * m], client_public_key)
        return ans + rsa.encrypt(msg[n * m:], client_public_key)

    def decrypt_me(self, message: bytes) -> str:
        return self.decrypt(message, self.server_keys_chain[1]).decode()

    def encrypt_me(self, message: bytes):
        return self.encrypt(message, self.client_public_RSA_key)

    def registration(self, message: str):
        print(message)
        current_login, current_password = message.split('\n')
        if self.dict_for_login_and_pass.get(current_login, None) is not None:
            self.connection.send(self.encrypt('This login is occupied'.encode(), self.client_public_RSA_key))
        else:
            self.dict_for_login_and_pass[current_login] = current_password
            os.mkdir('clients_files/' + current_login)
            with open(self.PATH_TO_LOGIN_PASSWORD, 'a') as f:
                f.write(current_login + '\t' + current_password + '\n')
            self.connection.send(self.encrypt('OK'.encode(), self.client_public_RSA_key))

    def log_in(self, message: str):
        print(message)
        current_login, current_password = message.split('\n')
        true_password = self.dict_for_login_and_pass.get(current_login, None)
        if true_password is None:
            self.connection.send(self.encrypt('This login is not exist'.encode(), self.client_public_RSA_key))
        elif current_password == true_password:
            self.login = current_login
            self.password = current_password
            self.connection.send(self.encrypt('OK'.encode(), self.client_public_RSA_key))
        else:
            self.connection.send(self.encrypt('Invalid password'.encode(), self.client_public_RSA_key))

    def get_notebook_list(self):
        files_list = '\n'.join(os.listdir(self.final_path_to_dir))
        self.connection.send(self.encrypt(files_list.encode(), self.client_public_RSA_key))

    def send_key(self, message: bytes):
        print(message)
        self.key_time = time.time()
        self.client_public_RSA_key = rsa.PublicKey.load_pkcs1(message)
        self.server_keys_chain = rsa.newkeys(self.KEY_LEN)
        self.connection.send(self.encrypt(self.server_keys_chain[0].save_pkcs1(), self.client_public_RSA_key))

    def open_file(self, message: str):
        print(message)
        finish_path_to_file = self.final_path_to_dir + '/' + message
        with open(finish_path_to_file, 'r') as f:
            self.connection.send(self.encrypt(f.read().encode(), self.client_public_RSA_key))

    def save_file(self, message: str):
        print(message)
        file_name, data = message.split('\n', 1)
        finish_path_to_file = self.final_path_to_dir + '/' + file_name
        with open(finish_path_to_file, 'w') as f:
            for b in data.encode():
                print(b)
            print(self.password.__hash__())
            f.write(data)
            self.connection.send(self.encrypt('Saved'.encode(), self.client_public_RSA_key))

    def delete_file(self, message: str):
        print(message)
        finish_path_to_file = self.final_path_to_dir + '/' + message
        os.remove(finish_path_to_file)
        self.connection.send(self.encrypt_me('Deleted'.encode()))
