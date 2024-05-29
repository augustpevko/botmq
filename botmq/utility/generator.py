import secrets

def generate_password() -> str:
    password_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    password_len = 8
    return ''.join(secrets.choice(password_chars) for _ in range(password_len))