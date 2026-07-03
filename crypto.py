from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64

# derives a fernet key from the users master password + their salt
# so the vault entries can only be decrypted with the master password
def derive_key(master_password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=bytes.fromhex(salt),
        iterations=200000,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode('utf-8')))

def encrypt_password(plain_text, key):
    fernet = Fernet(key)
    return fernet.encrypt(plain_text.encode('utf-8')).decode('utf-8')

def decrypt_password(token, key):
    fernet = Fernet(key)
    return fernet.decrypt(token.encode('utf-8')).decode('utf-8')
