"""
Crypto utilities for base64 encoding/decoding
"""

import base64
import json
from typing import Any, Dict, Union


def encode_base64(data: Any) -> str:
    """
    Encode data to base64 string.
    
    Args:
        data: Dictionary or JSON serializable object
        
    Returns:
        Base64 encoded string
    """
    if isinstance(data, dict):
        json_str = json.dumps(data)
    else:
        json_str = str(data)
    
    return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')


def decode_base64(encoded_data: str) -> Union[Dict, Any]:
    """
    Decode base64 string to data.
    
    Args:
        encoded_data: Base64 encoded string
        
    Returns:
        Decoded dictionary or object
        
    Raises:
        ValueError: If data cannot be decoded
    """
    try:
        decoded_bytes = base64.b64decode(encoded_data.encode('utf-8'))
        decoded_str = decoded_bytes.decode('utf-8')
        return json.loads(decoded_str)
    except Exception as e:
        raise ValueError(f"Failed to decode base64 data: {str(e)}")


def encode_response(data: Any) -> Dict[str, str]:
    """
    Encode response data as base64 wrapped in a dictionary.
    
    Args:
        data: Response data to encode
        
    Returns:
        Dictionary with 'encrypted' key containing base64 encoded data
    """
    return {
        "encrypted": encode_base64(data)
    }


def decode_request(encoded_data: str) -> Any:
    """
    Decode request data from base64.
    
    Args:
        encoded_data: Base64 encoded request data
        
    Returns:
        Decoded request data
    """
    return decode_base64(encoded_data)
