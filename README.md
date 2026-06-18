# 🔐 SecureFile — File Encryption & Decryption Tool

SecureFile is a complete, professional desktop application written in Python 3 using Tkinter for its GUI and AES-256 (via the cryptography Fernet library) for robust, authenticated file encryption and decryption.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents
1. [Features](#features)
2. [Screenshots](#screenshots)
3. [Installation](#installation)
4. [How to Use](#how-to-use)
5. [Technology Stack](#technology-stack)
6. [File Structure](#file-structure)
7. [Future Improvements](#future-improvements)
8. [License](#license)
9. [Author](#author)

---

## Features
- **Strong Key Derivation**: Uses PBKDF2HMAC with SHA-256, a 16-byte random salt, and 100,000 iterations to derive a secure 32-byte key from passwords.
- **Authenticated Encryption**: Uses Fernet (AES-256 in CBC mode with HMAC-SHA-256 verification) to guarantee file secrecy and integrity, preventing tampering.
- **Modern Dark Theme**: Styled with a premium dark navy color palette (`#1a1a2e` and `#16213e`) and clean layout typography.
- **Interactive Password Strength Indicator**: Real-time feedback on password strength (Weak, Medium, Strong) as the user types.
- **File Metadata Viewer**: Displays filename, human-readable size, file extension, and encryption status upon selection.
- **Copy Clipboard Button**: Easily copy the generated file output path on success.
- **Recent Activity Log**: Displays a history tracker list showing the last 3 files processed and their timestamp logs.
- **Secure Handling**: Passwords and keys are never stored anywhere on disk or cached long-term.

---

## Screenshots
Please see the `/screenshots` folder for user interface mockups and capture logs.

---

## Installation

Ensure you have Python 3 installed. You can check with `python --version`.

Clone the repository and install dependencies:
```bash
git clone https://github.com/karan942006/File-Encryption-Decryption-Tool.git
cd File-Encryption-Decryption-Tool
pip install -r requirements.txt
```

Launch the tool:
```bash
python main.py
```

> **Windows users:** Use `py main.py` if `python` is not in your PATH.

---

## How to Use
1. **Launch the Application**: Run `python main.py` from the terminal.
2. **Select a File**: Click the **Browse File** button to choose any document, image, or text file.
3. **Review Metadata**: The app dynamically loads and displays the file name, size, type, and status.
4. **Enter a Password**: Input a password in the password field. Use **Show Password** to toggle visibility. Watch the strength indicator — aim for **Strong** (green, 10+ chars).
5. **Encrypt or Decrypt**:
   - Click **🔒 Encrypt File** — saves a `.enc` file in the same folder.
   - Click **🔓 Decrypt File** — restores the original file (removes `.enc`).
6. **Copy Path**: On success, click **📋 Copy Path** to copy the output file location.
7. **View Activity**: Recent operations are logged in the **Recent Activity** panel.

---

## Technology Stack

| Tool / Dependency | Purpose |
| --- | --- |
| **Python 3** | Core language logic and runtime |
| **Tkinter** | Built-in library for desktop GUI |
| **cryptography (Fernet)** | AES-256 encryption + PBKDF2HMAC key derivation |

---

## File Structure

```text
File-Encryption-Decryption-Tool/
├── main.py              ← Launches the application
├── encryption.py        ← Cryptographic operations (Fernet, PBKDF2)
├── gui.py               ← Interface layout and widget behaviors
├── utils.py             ← Helper utility functions
├── requirements.txt     ← Package dependency listing
├── README.md            ← Application documentation
└── screenshots/         ← Empty folder for screenshots
```

---

## Future Improvements
- **Folder Encryption**: Support encrypting directory trees recursively.
- **Keyfile Authentication**: Optional physical key file verification alongside passwords.
- **Drag-and-Drop File Selection**: Integrate drag-and-drop extensions for easier file picking.
- **Progress Bars**: Real-time progress indicators for large files.
- **Cross-platform Installer**: `.dmg` for macOS and `.deb` for Linux.

---

## License
This project is licensed under the MIT License.

---

## Author
Made with ❤️ for Cybersecurity Course Final Project
