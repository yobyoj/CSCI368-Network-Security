import base64
import hashlib
import json
import socket
from sympy import isprime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Function to calculate the MAC (Message Authentication Code)
def mac(LK, g_r, C):
    lkBytes = LK.to_bytes(16, 'big')
    grBytes = g_r.to_bytes(16, 'big')
    concatenated_data = lkBytes + grBytes + C + lkBytes
    hash_result = hashlib.sha1(concatenated_data).hexdigest()
    return hash_result

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

# Function to read key values from a file
def read_key_values(file_path='key_values.txt'):
    with open(file_path, 'r') as file:
        key_values = [int(line.strip()) for line in file]
    return tuple(key_values)

# Read server data from the configuration file
with open('server.txt', 'r') as file:
    server_data = [line.strip() for line in file]

# Extract server information
if len(server_data) > 2:
    ip = server_data[0]
    port = int(server_data[1])
    pk_s = int(server_data[2])
else:
    print("Please configure server.txt with IP address and port number.")
    exit(1)

# Create a UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (ip, port)
s.bind(server_address)
print("Do Ctrl+c to exit the program !!")

CT_received = None  

while True:
    print("\n####### Server is listening #######")
    data, address = s.recvfrom(4096)
    print("\n2. Server received:")
    print("   - Data: ", data.decode('utf-8'))

    received_data = json.loads(data.decode('utf-8'))
    g_r_received, CT_received_str, MAC_received_str = received_data

    print("   - g_r received:", g_r_received)
    print("   - Base64 MAC received:", MAC_received_str)

    CT_received = base64.b64decode(CT_received_str)
    MAC_received = base64.b64decode(MAC_received_str)

    CT_received_str = CT_received_str
    CT_received = CT_received

    # Read key values from the file
    p, g, x_c, x_s, r = read_key_values()

    sk_c = x_c

    # Compute session key (TK) and long-term key (LK)
    TK_received = pow(g_r_received, sk_c, p)
    print("   - TK received:", TK_received)

    LK_received = pow(pk_s, sk_c, p)
    print("   - LK computed:", LK_received)

    # Compute MAC for verification
    MAC_prime = mac(LK_received, g_r_received, CT_received)
 
    MAC_received = MAC_received.decode('utf-8')
  
    # Verify MAC
    if MAC_received == MAC_prime:
        print("   - MAC verification successful. Continuing...")
        
        # Decrypt and print the received message
        M_prime = decryptSym(TK_received, CT_received)
        print("   - Decrypted Message:", M_prime)
    else:
        # If MAC verification fails, print error information
        M_prime = decryptSym(TK_received, CT_received)
        print("   - Decrypted Message:", M_prime)
        print("   - ERROR: MAC verification failed. Data integrity compromised.")
        print("     - MAC_received:", MAC_received)
        print("     - MAC calculated:", MAC_prime)
