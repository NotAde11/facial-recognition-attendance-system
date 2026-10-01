import json
import bcrypt
import os

USER_FILE = "users.json"

# Load users
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

# Save users
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# Hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Verify password
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# Register user
def register_user(username, password):
    users = load_users()
    
    if username in users:
        return False, "User already exists"
    
    users[username] = hash_password(password)
    save_users(users)
    
    return True, "User created"

# Login user
def login_user(username, password):
    users = load_users()
    
    if username not in users:
        return False, "User not found"
    
    if verify_password(password, users[username]):
        return True, "Login successful"
    
    return False, "Incorrect password"