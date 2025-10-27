# policy_engine.py

# Define policies: roles -> allowed actions/resources
POLICIES = {
    "admin": ["read_all", "write_all", "delete_all"],
    "user": ["read_own", "write_own"],
    "auditor": ["read_all"]
}

def check_permission(user_roles, action):
    """
    Checks if any of the user's roles allow the requested action.
    Returns True if allowed, False otherwise.
    """
    for role in user_roles:
        allowed_actions = POLICIES.get(role, [])
        if action in allowed_actions:
            return True
    return False
