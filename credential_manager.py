#!/usr/bin/env python3
"""
Encrypted Credentials Manager
Handles password-protected storage of sensitive configuration data
"""

import json
import os
import base64
import hashlib
import getpass
from tkinter import messagebox, simpledialog
from cryptography.fernet import Fernet  # pip install cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CredentialManager:
    """Manages encrypted storage of credentials and sensitive configuration"""
    
    def __init__(self, credentials_file="config_credentials.enc"):
        self.credentials_file = credentials_file
        self.credentials = {}
        self.is_encrypted = False
        
    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        password_bytes = password.encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password_bytes))
    
    def _generate_salt(self) -> bytes:
        """Generate a random salt for key derivation"""
        return os.urandom(16)
    
    def _is_file_encrypted(self, filepath: str) -> bool:
        """Check if file contains encrypted data"""
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Check for encryption markers
                return 'encrypted_data' in data and 'salt' in data
        except (json.JSONDecodeError, UnicodeDecodeError):
            # File exists but isn't valid JSON - might be binary encrypted
            return True
        except PermissionError:
            messagebox.showerror("Permission Error", f"Cannot access credentials file: {filepath}")
            return False
        except Exception:
            return False
    
    def load_credentials(self, parent_window=None):
        """Load credentials, handling encryption/decryption as needed"""
        if not os.path.exists(self.credentials_file):
            # No credentials file exists - prompt for initial setup
            return self._setup_initial_credentials(parent_window)
        
        self.is_encrypted = self._is_file_encrypted(self.credentials_file)
        
        try:
            if self.is_encrypted:
                return self._load_encrypted_credentials(parent_window)
            else:
                return self._load_unencrypted_credentials(parent_window)
                
        except PermissionError:
            messagebox.showerror("Permission Error", 
                               f"Cannot read credentials file: {self.credentials_file}")
            return False
        except Exception as e:
            messagebox.showerror("Credentials Error", 
                               f"Failed to load credentials: {str(e)}")
            return False
    
    def _setup_initial_credentials(self, parent_window):
        """Setup initial credentials with encryption option"""
        result = messagebox.askyesno(
            "Credentials Setup", 
            "No credentials file found.\n\n" +
            "Would you like to create an encrypted credentials file?\n\n" +
            "Yes: Create encrypted file (recommended)\n" +
            "No: Create unencrypted file"
        )
        
        if result:
            # Create encrypted
            password = self._prompt_for_new_password(parent_window)
            if password:
                self.is_encrypted = True
                self.credentials = self._get_default_credentials()
                return self.save_credentials(password)
        else:
            # Create unencrypted
            self.is_encrypted = False
            self.credentials = self._get_default_credentials()
            return self.save_credentials()
        
        return False
    
    def _get_default_credentials(self):
        """Get default credentials structure"""
        return {
            "openwebui": {
                "base_url": "http://172.16.27.122:3000",
                "api_key": "",
                "default_model": "",
                "temperature": 0.1,
                "max_tokens": 8000,
                "knowledge_collections": [],  # Store selected knowledge collections
                "last_used": None  # Timestamp of last use
            },
            "document_review": {
                "review_model": "llama3.1:latest",
                "comment_model": "llama3.1:latest",
                "tense_analysis_enabled": True,
                "interactive_comments": True
            },
            "advanced_features": {
                "rag_threshold": 10000,  # chars - above this use RAG, below use full prompt
                "auto_tense_correction": False,
                "backup_encrypted": True
            },
            "last_credential_file": None  # Track which credential file was last used
        }
    
    def _prompt_for_new_password(self, parent_window):
        """Prompt user for new password with confirmation"""
        password = simpledialog.askstring(
            "Create Password", 
            "Enter password for credentials encryption:",
            show='*',
            parent=parent_window
        )
        
        if not password:
            return None
            
        confirm = simpledialog.askstring(
            "Confirm Password",
            "Confirm password:",
            show='*',
            parent=parent_window
        )
        
        if password != confirm:
            messagebox.showerror("Password Error", "Passwords do not match!")
            return None
        
        if len(password) < 8:
            messagebox.showwarning("Password Warning", 
                                 "Password should be at least 8 characters long.")
        
        return password
    
    def _load_encrypted_credentials(self, parent_window):
        """Load and decrypt credentials with 3-strike password failure handling"""
        max_attempts = 3
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            attempts_remaining = max_attempts - attempt

            prompt_msg = "Enter password to decrypt credentials:"
            if attempt > 1:
                prompt_msg = f"Wrong password! {attempts_remaining} attempt(s) remaining:\n\nEnter password:"

            password = simpledialog.askstring(
                "Credentials Password",
                prompt_msg,
                show='*',
                parent=parent_window
            )

            if not password:
                # User cancelled
                if attempt < max_attempts:
                    result = messagebox.askyesno(
                        "Cancelled",
                        f"Password entry cancelled.\n\n{attempts_remaining} attempt(s) remaining.\n\nTry again?"
                    )
                    if not result:
                        break
                    continue
                else:
                    break

            try:
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    encrypted_data = json.load(f)

                salt = base64.urlsafe_b64decode(encrypted_data['salt'])
                encrypted_credentials = base64.urlsafe_b64decode(encrypted_data['encrypted_data'])

                key = self._derive_key_from_password(password, salt)
                fernet = Fernet(key)

                decrypted_data = fernet.decrypt(encrypted_credentials)
                self.credentials = json.loads(decrypted_data.decode('utf-8'))

                return True

            except Exception as e:
                if attempt >= max_attempts:
                    # All attempts failed - use blank credentials
                    messagebox.showerror(
                        "Access Denied",
                        "Failed to decrypt credentials after 3 attempts.\n\n" +
                        "Defaulting to blank credentials.\n" +
                        "You will need to re-enter your settings."
                    )
                    self.credentials = self._get_default_credentials()
                    self.is_encrypted = False  # Reset to unencrypted mode
                    return True  # Return True but with blank creds
                # Continue loop for retry

        # User gave up or cancelled
        messagebox.showwarning(
            "Credentials Not Loaded",
            "Using blank default credentials.\n" +
            "You will need to configure your settings."
        )
        self.credentials = self._get_default_credentials()
        self.is_encrypted = False
        return True
    
    def _load_unencrypted_credentials(self, parent_window):
        """Load unencrypted credentials and offer to encrypt"""
        try:
            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                self.credentials = json.load(f)

            # Offer to encrypt existing unencrypted file
            result = messagebox.askyesno(
                "Security Upgrade",
                "Your credentials file is unencrypted.\n\n" +
                "Would you like to encrypt it for better security?"
            )

            if result:
                password = self._prompt_for_new_password(parent_window)
                if password:
                    # Backup the unencrypted file before encrypting
                    import shutil
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    backup_path = f"{self.credentials_file}.unencrypted.backup.{timestamp}"
                    try:
                        shutil.copy2(self.credentials_file, backup_path)
                        print(f"✓ Backed up unencrypted file to: {backup_path}")
                    except Exception as e:
                        print(f"⚠ Could not backup unencrypted file: {e}")

                    self.is_encrypted = True
                    self.save_credentials(password)
                    messagebox.showinfo("Success",
                        f"Credentials encrypted successfully!\n\n" +
                        f"Original unencrypted file backed up to:\n{os.path.basename(backup_path)}")

            return True

        except json.JSONDecodeError:
            messagebox.showerror("File Error", "Credentials file is corrupted.")
            return False
    
    def save_credentials(self, password=None):
        """Save credentials, encrypted if password provided"""
        try:
            if self.is_encrypted and password:
                return self._save_encrypted_credentials(password)
            else:
                return self._save_unencrypted_credentials()
                
        except PermissionError:
            messagebox.showerror("Permission Error", 
                               f"Cannot write to credentials file: {self.credentials_file}")
            return False
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save credentials: {str(e)}")
            return False
    
    def _save_encrypted_credentials(self, password):
        """Encrypt and save credentials"""
        try:
            salt = self._generate_salt()
            key = self._derive_key_from_password(password, salt)
            fernet = Fernet(key)
            
            credentials_json = json.dumps(self.credentials, indent=2)
            encrypted_data = fernet.encrypt(credentials_json.encode('utf-8'))
            
            data_to_save = {
                'encrypted_data': base64.urlsafe_b64encode(encrypted_data).decode('utf-8'),
                'salt': base64.urlsafe_b64encode(salt).decode('utf-8'),
                'created': str(os.path.getctime(self.credentials_file)) if os.path.exists(self.credentials_file) else None,
                'version': '1.0'
            }
            
            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Encryption Error", f"Failed to encrypt credentials: {str(e)}")
            return False
    
    def _save_unencrypted_credentials(self):
        """Save unencrypted credentials"""
        with open(self.credentials_file, 'w', encoding='utf-8') as f:
            json.dump(self.credentials, f, indent=2)
        return True
    
    def get_credential(self, category, key, default=None):
        """Get a specific credential value"""
        return self.credentials.get(category, {}).get(key, default)
    
    def set_credential(self, category, key, value):
        """Set a credential value"""
        if category not in self.credentials:
            self.credentials[category] = {}
        self.credentials[category][key] = value
    
    def get_all_credentials(self):
        """Get all credentials"""
        return self.credentials.copy()
    
    def update_credentials(self, new_credentials):
        """Update credentials dictionary"""
        self.credentials.update(new_credentials)
    
    def change_password(self, parent_window=None):
        """Change encryption password"""
        if not self.is_encrypted:
            messagebox.showinfo("Info", "Credentials are not encrypted.")
            return False
        
        # Verify current password first
        current_password = simpledialog.askstring(
            "Current Password",
            "Enter current password:",
            show='*',
            parent=parent_window
        )
        
        if not current_password:
            return False
        
        # Try to decrypt with current password
        try:
            temp_file = f"{self.credentials_file}.temp"
            with open(self.credentials_file, 'r') as f:
                encrypted_data = json.load(f)
            
            salt = base64.urlsafe_b64decode(encrypted_data['salt'])
            encrypted_credentials = base64.urlsafe_b64decode(encrypted_data['encrypted_data'])
            
            key = self._derive_key_from_password(current_password, salt)
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_credentials)
            
            # Current password is correct, get new password
            new_password = self._prompt_for_new_password(parent_window)
            if new_password:
                # Save with new password
                if self.save_credentials(new_password):
                    messagebox.showinfo("Success", "Password changed successfully!")
                    return True
            
        except Exception:
            messagebox.showerror("Error", "Current password is incorrect.")
            return False
    
    def backup_credentials(self, backup_path=None):
        """Create backup of credentials file"""
        if not backup_path:
            backup_path = f"{self.credentials_file}.backup"

        try:
            import shutil
            shutil.copy2(self.credentials_file, backup_path)
            return True
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to backup credentials: {str(e)}")
            return False

    def load_credentials_from_file(self, filepath, parent_window=None):
        """Load credentials from a specific file"""
        if not os.path.exists(filepath):
            messagebox.showerror("File Error", f"File not found: {filepath}")
            return False

        # Temporarily change the credentials file path
        original_file = self.credentials_file
        self.credentials_file = filepath

        try:
            result = self.load_credentials(parent_window)
            if result:
                messagebox.showinfo("Success", f"Credentials loaded from:\n{os.path.basename(filepath)}")
            return result
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load credentials: {str(e)}")
            self.credentials_file = original_file
            return False
