from werkzeug.security import generate_password_hash, check_password_hash
import datetime

VAULT = {
    "alice": {"db_password": generate_password_hash("AliceDB@123"), "expires": None},
    "bob": {"db_password": generate_password_hash("BobDB@123"), "expires": None},
}

def issue_secret(username, secret_name, duration_minutes=5):
    user_vault = VAULT.get(username)
    if not user_vault or secret_name not in user_vault:
        return None
    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration_minutes)
    user_vault["expires"] = expiry_time
    return user_vault[secret_name]

def validate_secret(username, secret_name):
    user_vault = VAULT.get(username)
    if not user_vault or secret_name not in user_vault:
        return False, "Secret not found"
    if user_vault["expires"] and datetime.datetime.utcnow() > user_vault["expires"]:
        return False, "Secret expired"
    return True, "Access granted"
