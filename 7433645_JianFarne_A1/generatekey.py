import socket
import secrets
import random
import hashlib
import os

from sympy import isprime, primitive_root
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Function to calculate the MAC (Message Authentication Code)
def mac(LK, g, r, C):
    lkBytes = LK.to_bytes(16, 'big')
    grBytes = hex(pow(g, r, p))[2:].encode('utf-8')
    concatenated_data = (lkBytes + grBytes + C + lkBytes)
    hash_result = hashlib.sha1(concatenated_data).hexdigest()
    return hash_result

# Function to generate prime (p), primitive root (g), and private keys (x_c, x_s, r)
def genPG():
    while True:
        global p, g, x_s, x_c, r  
        p = secrets.randbits(128)
        r = random.randint(2, p-1)

        if p < 2 or not isprime(p):
            continue  

        g = secrets.randbelow(p)
        while pow(g, (p-1)//2, p) == 1 or pow(g, (p-1)//3, p) == 1:
            g = secrets.randbelow(p)

        x_c = secrets.randbelow(p)
        while pow(x_c, (p-1)//2, p) == 1 or pow(x_c, (p-1)//3, p) == 1:
            x_c = secrets.randbelow(p)
        
        x_s = secrets.randbelow(p)
        while pow(x_s, (p-1)//2, p) == 1 or pow(x_s, (p-1)//3, p) == 1:
            x_s = secrets.randbelow(p)

        print("Primitive root modulo p (g):", g)
      
        with open('key_values.txt', 'w') as file:
            file.write(f'{p}\n{g}\n{x_c}\n{x_s}\n{r}')

        return p, g, x_c, x_s

# Function to pad the message for encryption
def pad_message(message):
    block_size = 16  
    padding = block_size - len(message) % block_size
    return message + bytes([padding] * padding)

# Function to encrypt a message symmetrically
def encryptSym(key, message):
    key = key.to_bytes(16, 'big')  
    iv = os.urandom(16) 
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_message = pad_message(message.encode('utf-8'))
    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
    return iv + encrypted_message

# Function to decrypt a symmetrically encrypted message
def decryptSym(key, ciphertext):
    key = key.to_bytes(16, 'big') 
    iv = ciphertext[:16]  
    ciphertext = ciphertext[16:]  
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message_padded = decryptor.update(ciphertext) + decryptor.finalize()
    padding = decrypted_message_padded[-1]
    decrypted_message = decrypted_message_padded[:-padding].decode('utf-8')
    return decrypted_message

# Initialize global variables
p = 1
g = 1
x_c = 1
x_s = 1

# Generate prime (p), primitive root (g), and private keys (x_c, x_s, r)
genPG()
print("G: ", g)
print("P: ", p)
print("xc: ", x_c)
print("xs: ", x_s)

# Check if private keys are within the prime range
if x_s > p:
    print("xs > p")
else:
    print("OK")

if x_c > p:
    print("xc > p")
else:
    print("OK")

# Set server and client private/public keys
sk_s = x_s
pk_s = pow(g, x_s, p)

with open('server.txt', 'w') as file:
    file.write('127.0.0.1\n')
    file.write('5055\n')
    file.write(str(pk_s))

sk_c = x_c
pk_c = pow(g, x_c, p)

with open('client.txt', 'w') as file:
    file.write('127.0.0.1\n')
    file.write('5055\n')
    file.write(str(pk_c))

# Compute and print client and server long-term keys
LK = pow(pk_s, sk_c, p)
LK_client = pow(pk_c,sk_s,p)
print('LK of client', LK_client)
print("LK: ", LK)

# Compute and print session key (TK)
TK = pow(pk_s, r, p)
print(TK)

# Encrypt and print a sample message (CT)
message = "test"
CT = encryptSym(TK, message)
print("CT: ", CT.hex())

# Compute and print the MAC
MAC = mac(LK, g, r, CT)
print("MAC: ", MAC)

# Decrypt and print the message
decrypted_message = decryptSym(TK, CT)
print("Decrypted Message:", decrypted_message)
