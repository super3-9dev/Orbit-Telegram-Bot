from __future__ import annotations
import json
import os
from typing import Set, Dict, Any
from datetime import datetime
from pathlib import Path

class UserManager:
    """
    Manages user registration and storage for the arbitrage bot.
    Handles user registration, removal, and persistent storage.
    """
    
    def __init__(self, storage_file: str = "users.json"):
        self.storage_file = Path(storage_file)
        self.users: Set[int] = set()
        self.user_data: Dict[int, Dict[str, Any]] = {}
        self.load_users()
    
    def load_users(self) -> None:
        """Load registered users from storage file."""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = set(data.get('users', []))
                    self.user_data = data.get('user_data', {})
                print(f"[USER MANAGER] Loaded {len(self.users)} registered users")
            else:
                print("[USER MANAGER] No existing users file found, starting fresh")
        except Exception as e:
            print(f"[USER MANAGER] Error loading users: {e}")
            self.users = set()
            self.user_data = {}
    
    def save_users(self) -> None:
        """Save registered users to storage file."""
        try:
            data = {
                'users': list(self.users),
                'user_data': self.user_data,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[USER MANAGER] Saved {len(self.users)} users to storage")
        except Exception as e:
            print(f"[USER MANAGER] Error saving users: {e}")
    
    def register_user(self, user_id: int, username: str = None, first_name: str = None) -> bool:
        """
        Register a new user for arbitrage notifications.
        
        Args:
            user_id: Telegram user ID
            username: Telegram username (optional)
            first_name: User's first name (optional)
            
        Returns:
            bool: True if user was newly registered, False if already exists
        """
        print(f"[USER MANAGER] Attempting to register user {user_id} ({username or first_name or 'Unknown'})")
        print(f"[USER MANAGER] Current users: {self.users}")
        
        if user_id in self.users:
            print(f"[USER MANAGER] User {user_id} already registered")
            return False
        
        # Add user to the set
        self.users.add(user_id)
        
        # Store additional user data
        self.user_data[user_id] = {
            'registered_at': datetime.now().isoformat(),
            'username': username,
            'first_name': first_name,
            'last_notification': None,
            'total_notifications': 0
        }
        
        # Save to storage
        self.save_users()
        
        print(f"[USER MANAGER] New user registered: {user_id} ({username or first_name or 'Unknown'})")
        print(f"[USER MANAGER] Updated users: {self.users}")
        return True
    
    def unregister_user(self, user_id: int) -> bool:
        """
        Remove a user from arbitrage notifications.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            bool: True if user was removed, False if not found
        """
        if user_id not in self.users:
            return False
        
        # Remove user from set and data
        self.users.remove(user_id)
        if user_id in self.user_data:
            del self.user_data[user_id]
        
        # Save to storage
        self.save_users()
        
        print(f"[USER MANAGER] User unregistered: {user_id}")
        return True
    
    def is_registered(self, user_id: int) -> bool:
        """Check if a user is registered for notifications."""
        return user_id in self.users
    
    def get_registered_users(self) -> Set[int]:
        """Get all registered user IDs."""
        return self.users.copy()
    
    def get_user_count(self) -> int:
        """Get total number of registered users."""
        return len(self.users)
    
    def update_user_activity(self, user_id: int) -> None:
        """Update user's last notification timestamp and count."""
        if user_id in self.user_data:
            self.user_data[user_id]['last_notification'] = datetime.now().isoformat()
            self.user_data[user_id]['total_notifications'] += 1
    
    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """Get information about a specific user."""
        return self.user_data.get(user_id, {})
    
    def get_all_user_info(self) -> Dict[int, Dict[str, Any]]:
        """Get information about all users."""
        return self.user_data.copy()
