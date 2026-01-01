from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def generate_symmetric_key(bit_length: int =256) -> bytes:
    """Generate a random AES key. bit_length must be128,192 or256."""
    if bit_length not in (128,192,256):
        raise ValueError("bit_length must be one of128,192,256")
    return AESGCM.generate_key(bit_length=bit_length)

def symmetric_encrypt(aes_key: bytes, data: bytes) -> dict:
    """Encrypt data with AES-GCM using the provided symmetric key.

    Returns a dict with `nonce` and `ciphertext` (which includes the authentication tag).
    """
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12) #96-bit nonce recommended for GCM
    ciphertext = aesgcm.encrypt(nonce, data, associated_data=None)
    return {"nonce": nonce, "ciphertext": ciphertext}

def symmetric_decrypt(aes_key: bytes, blob: dict) -> bytes:
    """Decrypt a blob produced by `symmetric_encrypt` using the same AES key."""
    aesgcm = AESGCM(aes_key)
    return aesgcm.decrypt(blob["nonce"], blob["ciphertext"], associated_data=None)