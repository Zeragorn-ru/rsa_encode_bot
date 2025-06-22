# -*- coding: utf-8 -*-
import base64

from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes


# Функции шифрования и генерации ключей
def generate_rsa_keys() -> (str, str):
    key = RSA.generate(2048)
    private_key = key.export_key().decode()
    public_key = key.publickey().export_key().decode()
    return public_key, private_key

def encrypt_text(text: str, public_key: str) -> str:
    aes_key = get_random_bytes(32)
    rsa_cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
    encrypted_aes_key = rsa_cipher.encrypt(aes_key)
    aes_cipher = AES.new(aes_key, AES.MODE_GCM)

    try:
        ciphertext, tag = aes_cipher.encrypt_and_digest(text.encode())
    except AttributeError:
        return "Это не текст"

    return base64.b64encode(
        encrypted_aes_key + aes_cipher.nonce + tag + ciphertext
    ).decode()

def decrypt_text(encrypted_data: str, private_key: str) -> str:
    try:
        encrypted_data = base64.b64decode(encrypted_data)
        rsa_key_size = 256
        encrypted_aes_key = encrypted_data[:rsa_key_size]
        nonce = encrypted_data[rsa_key_size:rsa_key_size + 16]
        tag = encrypted_data[rsa_key_size + 16:rsa_key_size + 32]
        ciphertext = encrypted_data[rsa_key_size + 32:]
        rsa_cipher = PKCS1_OAEP.new(RSA.import_key(private_key))
        aes_key = rsa_cipher.decrypt(encrypted_aes_key)
        aes_cipher = AES.new(aes_key, AES.MODE_GCM, nonce=nonce)
        return aes_cipher.decrypt_and_verify(ciphertext, tag).decode()
    except Exception:
        return "Это не текст"

def is_pem_key(text: str) -> bool:
    return any(x in text for x in [
        "-----BEGIN PUBLIC KEY-----",
        "-----BEGIN PRIVATE KEY-----",
        "-----BEGIN RSA PRIVATE KEY-----"
    ])
