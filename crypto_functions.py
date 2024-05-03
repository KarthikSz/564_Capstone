from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode
import hashlib

def create_cipher(key):
    key_hash = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(key_hash, AES.MODE_CBC)
    return cipher, b64encode(cipher.iv).decode('utf-8')

def encrypt_data(data, key):
    cipher, iv = create_cipher(key)
    ct_bytes = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    ct = b64encode(ct_bytes).decode('utf-8')
    return iv + ct

def decrypt_data(encrypted_data, key):
    iv = b64decode(encrypted_data[:24])
    ct = b64decode(encrypted_data[24:])
    key_hash = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(key_hash, AES.MODE_CBC, iv)
    try:
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode()
    except ValueError as e:
        print("Decryption error:", e)
        return None

