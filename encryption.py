# =====================================================================
# SECURITY NOTES:
# 1. Why PBKDF2HMAC is used instead of a simple hash:
#    A simple hash like SHA-256 is fast and susceptible to high-speed GPU-accelerated
#    brute-force and precomputed rainbow table attacks. PBKDF2HMAC uses key stretching
#    with 100,000 iterations to make brute-forcing password keys computationally infeasible.
# 2. Why salt is random and stored with the file:
#    The 16-byte random salt is generated via a cryptographically secure source (os.urandom).
#    It guarantees that identical passwords produce different encryption keys. The salt is 
#    stored at the start of the encrypted file because it is required during decryption.
# 3. Why Fernet is used:
#    Fernet provides Authenticated Encryption (AES-256 in CBC mode combined with HMAC-SHA256).
#    It guarantees that ciphertext cannot be read or modified (tampered with) without the key.
# 4. Password storage:
#    The password is NEVER saved to disk or stored long-term in memory, preventing leaks.
# =====================================================================

import base64
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken

def generate_key(password: str, salt: bytes) -> bytes:
    """
    Derives a url-safe base64 key from password and salt using PBKDF2HMAC.
    """
    try:
        # Key stretching configuration: SHA-256, 100k iterations, 32-byte key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        # Convert password to bytes and derive
        derived_key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(derived_key)
    except Exception as e:
        print(f"Key generation failed: {e}")
        raise

def encrypt_file(file_path: str, password: str) -> str:
    """
    Encrypts file content using Fernet and saves it as file_path.enc.
    """
    try:
        # Generate 16-byte random salt for key generation
        salt = os.urandom(16)
        key = generate_key(password, salt)
        fernet = Fernet(key)
        
        # Read the target file content in binary format
        with open(file_path, 'rb') as f:
            original_data = f.read()
            
        encrypted_data = fernet.encrypt(original_data)
        output_path = file_path + ".enc"
        
        # Write salt (16 bytes) first, then append ciphertext
        with open(output_path, 'wb') as f:
            f.write(salt + encrypted_data)
            
        return output_path
    except FileNotFoundError as e:
        print(f"File not found for encryption: {file_path}")
        raise FileNotFoundError(f"The file '{file_path}' was not found.") from e
    except PermissionError as e:
        print(f"Permission denied for encryption: {file_path}")
        raise PermissionError(f"Permission denied to write output file.") from e
    except Exception as e:
        print(f"Encryption error: {e}")
        raise ValueError(f"Encryption failed: {e}") from e

def decrypt_file(file_path: str, password: str) -> str:
    """
    Decrypts a file with password and salt from file header.
    """
    try:
        # Read file binary contents
        with open(file_path, 'rb') as f:
            salt = f.read(16)
            encrypted_data = f.read()
            
        if len(salt) < 16:
            raise ValueError("Invalid file structure (missing 16-byte salt).")
            
        key = generate_key(password, salt)
        fernet = Fernet(key)
        
        try:
            decrypted_data = fernet.decrypt(encrypted_data)
        except InvalidToken as e:
            # Raise custom ValueError on wrong password / decryption failure
            raise ValueError("Incorrect password. Decryption failed.") from e
            
        # Determine output file path (strip .enc)
        output_path = file_path[:-4] if file_path.lower().endswith('.enc') else file_path + ".dec"
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
            
        return output_path
    except FileNotFoundError as e:
        print(f"File not found for decryption: {file_path}")
        raise FileNotFoundError(f"The file '{file_path}' was not found.") from e
    except PermissionError as e:
        print(f"Permission denied for decryption: {file_path}")
        raise PermissionError(f"Permission denied to access or write file.") from e
    except ValueError as e:
        print(f"Decryption assertion error: {e}")
        raise
    except Exception as e:
        print(f"Unexpected decryption error: {e}")
        raise ValueError(f"Decryption failed: {e}") from e
