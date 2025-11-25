"""SQLite user and refresh token repository."""
import sqlite3
from datetime import datetime
from typing import Optional
from app.application.services.user_service import UserModel, RefreshTokenModel


class SQLiteUserRepository:
    """Repository for user operations."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create user and refresh_tokens tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                revoked INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id)")
        
        conn.commit()
        conn.close()
    
    def create_user(self, user: UserModel) -> int:
        """Create a new user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, username, hashed_password, is_active) VALUES (?, ?, ?, ?)",
            (user.email, user.username, user.hashed_password, 1 if user.is_active else 0)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return UserModel(
                id=row[0], email=row[1], username=row[2],
                hashed_password=row[3], is_active=bool(row[4]),
                created_at=datetime.fromisoformat(row[5]) if row[5] else None
            )
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[UserModel]:
        """Get user by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return UserModel(
                id=row[0], email=row[1], username=row[2],
                hashed_password=row[3], is_active=bool(row[4]),
                created_at=datetime.fromisoformat(row[5]) if row[5] else None
            )
        return None
    
    def store_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> int:
        """Store a refresh token."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user_id, token, expires_at.isoformat())
        )
        token_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return token_id
    
    def get_refresh_token(self, token: str) -> Optional[RefreshTokenModel]:
        """Get refresh token by value."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM refresh_tokens WHERE token = ? AND revoked = 0", (token,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return RefreshTokenModel(
                id=row[0], user_id=row[1], token=row[2],
                expires_at=datetime.fromisoformat(row[3]),
                revoked=bool(row[4]),
                created_at=datetime.fromisoformat(row[5]) if row[5] else None
            )
        return None
    
    def revoke_refresh_token(self, token: str):
        """Revoke a refresh token."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE refresh_tokens SET revoked = 1 WHERE token = ?", (token,))
        conn.commit()
        conn.close()
    
    def revoke_all_user_tokens(self, user_id: int):
        """Revoke all refresh tokens for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE refresh_tokens SET revoked = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
