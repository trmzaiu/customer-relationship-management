import hashlib
import json
import os

USER_DB_FILE = 'user_db.json'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_user_db():
    if not os.path.exists(USER_DB_FILE):
        # Tạo file mới với tài khoản admin mặc định
        default_db = {"admin": hash_password("admin123")}
        with open(USER_DB_FILE, 'w') as f:
            json.dump(default_db, f)
    with open(USER_DB_FILE, 'r') as f:
        return json.load(f)

def save_user_db(user_db):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(user_db, f)
