import re

def validate_username(username):
    if not username or len(username) < 3 or len(username) > 20:
        return False
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    return True

def validate_password(password):
    if not password or len(password) < 6 or len(password) > 20:
        return False
    if not re.match(r'^[a-zA-Z0-9@#$%^&+=]+$', password):
        return False
    return True

def validate_email(email):
    if not email or len(email) > 120:
        return False
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return False
    return True 