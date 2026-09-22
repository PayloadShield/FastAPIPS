import json
from typing import Any, Dict, Optional

from .EncryptionHandler import EncryptionHandler
from cryptography.fernet import Fernet

# ============================================================================
# Fernet Encryption Handler
# ============================================================================

class FernetEncryptionHandler(EncryptionHandler):
    """
    Fernet symmetric encryption handler.
    Requires "Key" to be set via PayloadShieldEnc.init({"Key": ...}).
    """

    def encode(self, data: Any, config: Optional[Dict[str, Any]] = None) -> str:
        cipher = Fernet(self._get_key(config))
        payload = json.dumps(data).encode("utf-8")
        return cipher.encrypt(payload).decode("utf-8")

    def decode(self, encoded_data: str, config: Optional[Dict[str, Any]] = None) -> Any:
        cipher = Fernet(self._get_key(config))
        try:
            payload = cipher.decrypt(encoded_data.encode("utf-8"))
            return json.loads(payload.decode("utf-8"))
        except Exception as e:
            raise ValueError(f"Failed to decode fernet data: {str(e)}")

    @staticmethod
    def _get_key(config: Optional[Dict[str, Any]]) -> bytes:
        key = (config or {}).get("Key")
        if not key:
            raise ValueError(
                "Fernet encryption requires 'Key' to be set via "
                "PayloadShieldEnc.init({'Key': ...})"
            )
        return key.encode("utf-8") if isinstance(key, str) else key