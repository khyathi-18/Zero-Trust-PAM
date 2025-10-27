from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os
from policy_engine import check_permission
from vault import issue_secret
from logger import log_event

app = Flask(__name__)

SECRET_KEY = os.environ.get("JWT_SECRET", "dev-secret-key")

USERS = {
    "alice": {"password": generate_password_hash("Password1!"), "roles": ["admin"], "mfa_enabled": False},
    "bob": {"password": generate_password_hash("Password2!"), "roles": ["user"], "mfa_enabled": False},
}

def create_jwt(username, roles):
    payload = {
        "sub": username,
        "roles": roles,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = USERS.get(username)
    if not user:
        log_event(username, "/login", "login_attempt", "failed_user_not_found")
        return jsonify({"error": "User not found"}), 404

    if not check_password_hash(user["password"], password):
        log_event(username, "/login", "login_attempt", "failed")
        return jsonify({"error": "Incorrect password"}), 401

    if user["mfa_enabled"] and not data.get("mfa_token"):
        log_event(username, "/login", "login_attempt", "mfa_required")
        return jsonify({"mfa_required": True, "message": "MFA token required"}), 200

    token = create_jwt(username, user["roles"])
    log_event(username, "/login", "login_attempt", "success")
    return jsonify({"access_token": token}), 200

@app.route("/protected", methods=["GET"])
def protected():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Missing token"}), 401
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return jsonify({"error": "Invalid authorization header"}), 401
    token = parts[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    log_event(payload["sub"], "/protected", "access_protected", "success")
    return jsonify({"message": f"Hello {payload['sub']}, your roles: {payload['roles']}"}), 200

@app.route("/action/<action_name>", methods=["GET"])
def perform_action(action_name):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Missing token"}), 401
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return jsonify({"error": "Invalid authorization header"}), 401
    token = parts[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    if not check_permission(payload["roles"], action_name):
        log_event(payload["sub"], f"/action/{action_name}", "action_performed", "denied")
        return jsonify({"error": f"Access denied for action '{action_name}'"}), 403

    log_event(payload["sub"], f"/action/{action_name}", "action_performed", "success")
    return jsonify({"message": f"Action '{action_name}' performed successfully!"}), 200

@app.route("/vault/<secret_name>", methods=["GET"])
def get_secret(secret_name):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Missing token"}), 401
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return jsonify({"error": "Invalid authorization header"}), 401
    token = parts[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401

    if not check_permission(payload["roles"], "read_all"):
        log_event(payload["sub"], f"/vault/{secret_name}", "vault_access", "denied")
        return jsonify({"error": "Access denied"}), 403

    secret = issue_secret(payload["sub"], secret_name)
    if not secret:
        log_event(payload["sub"], f"/vault/{secret_name}", "vault_access", "failed")
        return jsonify({"error": "Secret not found"}), 404

    log_event(payload["sub"], f"/vault/{secret_name}", "vault_access", "success")
    return jsonify({"secret": secret}), 200

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Zero Trust PAM API running"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
