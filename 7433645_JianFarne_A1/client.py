import base64
import json
import random
import socket
import secrets
import hashlib
import os

from sympy import isprime, primitive_root
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def pad_message(message):
    # Pad the message to make its length a multiple of block size
    block_size = 16
    padding = block_size - len(message) % block_size
    return message + bytes([padding] * padding)

def encryptSym(key, message):
    # Encrypt the message using AES in CFB mode
    key = key.to_bytes(16, 'big')
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_message = pad_message(message.encode('utf-8'))
    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
    return iv + encrypted_message

def mac(LK, g, r, CT, p):
    # Compute the MAC using SHA-1 hash
    lkBytes = LK.to_bytes(16, 'big')
    grBytes = pow(g, r, p).to_bytes(16, 'big')

    if not isinstance(CT, bytes):
        CT = CT.encode('utf-8')

    concatenated_data = lkBytes + grBytes + CT + lkBytes
    hash_result = hashlib.sha1(concatenated_data).hexdigest()
    return hash_result

def read_key_values(file_path='key_values.txt'):
    # Read key values from a file
    with open(file_path, 'r') as file:
        key_values = [int(line.strip()) for line in file]
    return tuple(key_values)

def send_data_to_server(message, local_pk, server_address):
    # Send encrypted message and MAC to the server
    p, g, x_c, x_s, r = read_key_values()
    pk_c = pow(g, x_s, p)
    sk_c = x_c
    LK = pow(pk_c, sk_c, p)
    TK = pow(local_pk, r, p)
    CT = encryptSym(TK, message)
    MAC = mac(LK, g, r, CT, p)
    CT_base64 = base64.b64encode(CT).decode('utf-8')
    MAC_base64 = base64.b64encode(MAC.encode('utf-8')).decode('utf-8')
    sender_data = (pow(g, r, p), CT_base64, MAC_base64)
    s.sendto(json.dumps(sender_data).encode('utf-8'), server_address)

def read_config_file(file_path):
    # Read server configuration from a file
    with open(file_path, 'r') as file:
        config_data = [line.strip() for line in file]
    return config_data

# Create a UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)

# Read client configuration
config_file_path = 'client.txt'
config_data = read_config_file(config_file_path)
ip = config_data[0]
port = int(config_data[1])
local_pk = int(config_data[2])
server_address = (ip, port)

# Main loop to send messages to the server
while True:
    user_input = input("Type some text to send =>")
    send_data_to_server(user_input, local_pk, server_address)
    print("\n\n 1. Client Sent: ", user_input, "\n\n")
    data, address = s.recvfrom(4096)
    print("\n\n 2. Client received: ", data.decode('utf-8'), "\n\n")

# Close the socket when done
s.close()
