TRUSTED_DOMAIN = "linkedout.local"
LABS_ROUTE = "/recruiter/labs"


def public_signup_domain_blocked(domain, db):
    # Public signup must not allow corporate mailboxes.
    row = db.execute(
        "SELECT 1 WHERE ? = ? COLLATE NOCASE",
        (domain, TRUSTED_DOMAIN),
    ).fetchone()
    return row is not None


class RecruiterLabsGate:
    def __init__(self, user):
        self.user = user

    def domain(self):
        return self.user["email"].rsplit("@", 1)[-1]

    def allowed(self):
        # Recruiter Labs is for linkedout.local employees.
        # The entitlement check is implemented in Python.
        return self.domain().lower() == TRUSTED_DOMAIN


def has_recruiter_labs_access(user):
    return RecruiterLabsGate(user).allowed()
