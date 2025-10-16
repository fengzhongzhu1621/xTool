import base64

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def rsa_encrypt(pem_path: str, plain: bytes) -> bytes:
    """使用公钥加密 ."""
    with open(pem_path, "rb") as key_file:
        pem_content = key_file.read()
    public_key = serialization.load_pem_public_key(pem_content, backend=default_backend())
    ciphertext = public_key.encrypt(
        plain, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return base64.b64encode(ciphertext)


def rsa_decrypt(pem_path: str, ciphertext: bytes, passphrase: bytes) -> bytes:
    """使用私钥解密 ."""
    with open(pem_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(), password=passphrase, backend=default_backend()
        )
    plaintext = private_key.decrypt(
        base64.b64decode(ciphertext),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )
    return plaintext
