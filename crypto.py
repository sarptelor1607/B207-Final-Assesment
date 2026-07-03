from cryptography.fernet import Fernet
import hashlib
import base64

SECRET_KEY = 'B207-vault-secret-key-2024'

# fernet needs a 32 byte base64 key so we hash our secret to get one
key = base64.urlsafe_b64encode(hashlib.sha256(SECRET_KEY.encode('utf-8')).digest())
fernet = Fernet(key)

def encrypt_password(plain_text):
    return fernet.encrypt(plain_text.encode('utf-8')).decode('utf-8')

def decrypt_password(token):
    return fernet.decrypt(token.encode('utf-8')).decode('utf-8')
