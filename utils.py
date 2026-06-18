import os

def get_file_size(file_path: str) -> str:
    """
    Returns the file size in a human-readable format (e.g., KB, MB, GB).
    """
    try:
        if not os.path.exists(file_path):
            return "0 Bytes"
        size_bytes = os.path.getsize(file_path)
        if size_bytes == 0:
            return "0 Bytes"
        
        # Define units for size scaling
        units = ["Bytes", "KB", "MB", "GB", "TB"]
        i = 0
        # Divide by 1024 to convert to next unit size
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024.0
            i += 1
            
        # Format output to 2 decimal places for KB/MB/GB/TB
        if i > 0:
            return f"{size_bytes:.2f} {units[i]}"
        return f"{size_bytes} {units[i]}"
    except Exception as e:
        # Log error to console for debugging
        print(f"Error calculating file size for {file_path}: {e}")
        return "Unknown Size"

def get_file_extension(file_path: str) -> str:
    """
    Returns the file extension in uppercase (e.g., 'TXT', 'PDF').
    If no extension, returns 'NONE'.
    """
    try:
        # Extract extension from path
        _, ext = os.path.splitext(file_path)
        if ext:
            # Strip the leading dot and convert to uppercase
            return ext[1:].upper()
        return "NONE"
    except Exception as e:
        # Log error to console for debugging
        print(f"Error getting file extension for {file_path}: {e}")
        return "UNKNOWN"

def is_encrypted_file(file_path: str) -> bool:
    """
    Returns True if the file path ends with '.enc' (case-insensitive).
    """
    try:
        return file_path.lower().endswith('.enc')
    except Exception as e:
        # Log error to console for debugging
        print(f"Error checking if file {file_path} is encrypted: {e}")
        return False

def get_file_name(file_path: str) -> str:
    """
    Returns the base filename without the full directory path.
    """
    try:
        # Get standard base name from path
        return os.path.basename(file_path)
    except Exception as e:
        # Log error to console for debugging
        print(f"Error extracting file name for {file_path}: {e}")
        return ""
