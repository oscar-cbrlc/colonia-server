import os
import base64
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from config import settings

KEY_ID = settings.chat_encryption_key_id
KEY = base64.urlsafe_b64decode(settings.chat_encryption_key)
aesgcm = AESGCM(KEY)

def build_associated_data(
    team_id: int,
    user_id: Optional[int],
    triggered_by: Optional[int],
    message_type: int
) -> bytes:
    """Construye y codifica los datos de autentificación asociados de un mensaje"""
    user = str(user_id) if user_id is not None else "system"
    actor = str(triggered_by) if triggered_by is not None else "none"

    return (
        f"team-chat:v1:{team_id}:{user}:{actor}:{message_type}:{KEY_ID}"
    ).encode("utf-8")

def encrypt_message(
    message: str,
    team_id: int,
    user_id: Optional[int],
    triggered_by: Optional[int],
    message_type: int
) -> str:
    """Cifra el contenido de un mensaje"""

    nonce = os.urandom(12)
    aad = build_associated_data(
        team_id,
        user_id,
        triggered_by,
        message_type
    )

    encrypted = aesgcm.encrypt(
        nonce,
        message.encode("utf-8"),
        aad
    )

    payload = nonce + encrypted
    encoded = base64.urlsafe_b64encode(payload).decode("utf-8")
    return f"v1:{KEY_ID}:{encoded}"


def decrypt_message(
    encrypted_message: str,
    team_id: int,
    user_id: Optional[int],
    triggered_by: Optional[int],
    message_type: int
) -> str:
    """Decifra el contenido de un mensaje"""

    version, key_id, encoded = encrypted_message.split(":", 2)

    if version != "v1":
        raise ValueError("Versión de cifrado no compatible")

    if key_id != KEY_ID:
        raise ValueError("Clave de cifrado no disponible")

    payload = base64.urlsafe_b64decode(encoded)

    nonce = payload[:12]
    ciphertext = payload[12:]

    aad = build_associated_data(
        team_id,
        user_id,
        triggered_by,
        message_type
    )

    return aesgcm.decrypt(
        nonce,
        ciphertext,
        aad
    ).decode("utf-8")
