import json
import os
import base64
import struct
import zlib
from .constants import SAVE_PATH

_XOR_KEY = 0xC7
_MAGIC = b"PCLICKER1"


def _protect(data):
    raw = _MAGIC + data
    checksum = struct.pack(">I", zlib.crc32(raw) & 0xFFFFFFFF)
    payload = raw + checksum
    obfuscated = bytes(b ^ _XOR_KEY for b in payload)
    return base64.b64encode(obfuscated)


def _unprotect(encoded):
    obfuscated = base64.b64decode(encoded)
    payload = bytes(b ^ _XOR_KEY for b in obfuscated)
    if len(payload) < 12:
        return None
    stored_checksum = struct.unpack(">I", payload[-4:])[0]
    raw = payload[:-4]
    if zlib.crc32(raw) & 0xFFFFFFFF != stored_checksum:
        return None
    if not raw.startswith(_MAGIC):
        return None
    return raw[len(_MAGIC):]


def save_game(state):
    try:
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        json_bytes = json.dumps(state.to_dict()).encode("utf-8")
        tmp = SAVE_PATH + ".tmp"
        with open(tmp, "wb") as f:
            f.write(_protect(json_bytes))
        os.replace(tmp, SAVE_PATH)
    except (IOError, OSError) as e:
        print(f"Erro ao salvar: {e}")


def load_game(state):
    if not os.path.exists(SAVE_PATH):
        return
    try:
        with open(SAVE_PATH, "rb") as f:
            encoded = f.read()
        raw = _unprotect(encoded)
        if raw is None:
            print("Save corrompido ou adulterado — ignorando")
            return
        data = json.loads(raw.decode("utf-8"))
        state.from_dict(data)
    except (json.JSONDecodeError, UnicodeDecodeError, IOError, OSError) as e:
        print(f"Erro ao carregar save: {e}")
