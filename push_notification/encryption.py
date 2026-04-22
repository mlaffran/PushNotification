# ********************************************************************************
# *                                                                              *
# *   This program is free software; you can redistribute it and/or modify       *
# *   it under the terms of the GNU General Public License (GPL)                 *
# *   as published by the Free Software Foundation; version 3 of the License.    *
# *   for detail see the LICENSE text file.                                      *
# *                                                                              *
# *   This program is distributed in the hope that it will be useful,            *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of             *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                       *
# *   See the GNU General Public License for more details.                       *
# *                                                                              *
# *   You should have received a copy of the GNU General Public License          *
# *   License along with this program; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston,                      *
# *   MA 02111-1307, USA                                                         *
# *_____________________________________________________________________________ *
# *                                                                              *
# *     ##########################################################               *
# * ## PushNotification FreeCAD WorkBench 2026.04.09-V01 ##                     *
# *     ##########################################################               *
# *                                                                              *
# *                   Authors of this workbench:                                 *
# *           Marco Laffranchi <Laffranchi.Marco@gmail.com>                      *
# *                                                                              *
# *          Please refer to the Documentation and README for                    *
# *      more information regarding this WorkBench and its usage                 *
# *                                                                              *
# ********************************************************************************
"""Encryption utilities for machine-specific file encryption."""

import base64
import hashlib
import json
import os
import platform
import socket
import uuid
from typing import Any, Dict, Optional


def get_machine_id() -> str:
    """Get a machine-specific identifier."""
    # Combine hostname, platform, and machine architecture
    hostname = socket.gethostname()
    system = platform.system()
    machine = platform.machine()
    # Try to get MAC address if available
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                       for elements in range(0, 8*6, 8)][::-1])
    except:
        mac = "unknown"
    
    # Create a unique machine ID string
    machine_id = f"{hostname}:{system}:{machine}:{mac}"
    return machine_id


def derive_key(machine_id: str, salt: bytes = b"") -> bytes:
    """Derive an encryption key from machine ID."""
    if not salt:
        salt = b"PushNotificationSalt"
    # Use PBKDF2 to derive a key
    key = hashlib.pbkdf2_hmac(
        'sha256',
        machine_id.encode('utf-8'),
        salt,
        100000,  # Number of iterations
        dklen=32  # Length of derived key
    )
    return key


def simple_xor_encrypt(data: bytes, key: bytes) -> bytes:
    """Simple XOR encryption (not cryptographically secure but good enough for our purpose)."""
    key_len = len(key)
    encrypted = bytearray()
    for i, byte in enumerate(data):
        encrypted.append(byte ^ key[i % key_len])
    return bytes(encrypted)


def simple_xor_decrypt(data: bytes, key: bytes) -> bytes:
    """XOR decryption (same as encryption)."""
    return simple_xor_encrypt(data, key)


def encrypt_data(data: Dict[str, Any]) -> str:
    """Encrypt data dictionary for current machine."""
    machine_id = get_machine_id()
    key = derive_key(machine_id)
    
    # Convert data to JSON
    json_str = json.dumps(data)
    json_bytes = json_str.encode('utf-8')
    
    # Encrypt with XOR
    encrypted = simple_xor_encrypt(json_bytes, key)
    
    # Encode with base64
    encoded = base64.b64encode(encrypted).decode('ascii')
    
    # Include machine ID hash for verification
    machine_hash = hashlib.sha256(machine_id.encode('utf-8')).hexdigest()[:16]
    
    return f"{machine_hash}:{encoded}"


def decrypt_data(encrypted_str: str) -> Optional[Dict[str, Any]]:
    """Decrypt data, returns None if not created on this machine."""
    try:
        if ':' not in encrypted_str:
            return None
            
        machine_hash, encoded = encrypted_str.split(':', 1)
        
        # Check if this machine matches
        current_machine_id = get_machine_id()
        current_machine_hash = hashlib.sha256(current_machine_id.encode('utf-8')).hexdigest()[:16]
        
        if machine_hash != current_machine_hash:
            # Not the same machine
            return None
        
        # Decode base64
        encrypted = base64.b64decode(encoded)
        
        # Derive key
        key = derive_key(current_machine_id)
        
        # Decrypt
        decrypted = simple_xor_decrypt(encrypted, key)
        
        # Parse JSON
        json_str = decrypted.decode('utf-8')
        data = json.loads(json_str)
        
        return data
    except Exception:
        return None


def save_notification_link_to_file(document_path: str, notification_link: str) -> bool:
    """Save notification link to .PushNotification file in document folder."""
    try:
        if not document_path:
            return False
            
        # Get document directory
        doc_dir = os.path.dirname(document_path)
        if not doc_dir:
            return False
            
        file_path = os.path.join(doc_dir, ".PushNotification")
        
        # Prepare data
        data = {
            "version": 1,
            "notification_link": notification_link,
            "created_on": get_machine_id()
        }
        
        # Encrypt and save
        encrypted = encrypt_data(data)
        
        with open(file_path, 'w') as f:
            f.write(encrypted)
            
        return True
    except Exception:
        return False


def load_notification_link_from_file(document_path: str) -> Optional[str]:
    """Load notification link from .PushNotification file."""
    try:
        if not document_path:
            return None
            
        # Get document directory
        doc_dir = os.path.dirname(document_path)
        if not doc_dir:
            return None
            
        file_path = os.path.join(doc_dir, ".PushNotification")
        
        if not os.path.exists(file_path):
            return None
            
        with open(file_path, 'r') as f:
            encrypted_str = f.read().strip()
            
        data = decrypt_data(encrypted_str)
        if data is None:
            # Could not decrypt (different machine)
            return None
            
        return data.get("notification_link")
    except Exception:
        return None