import re
import bcrypt

from services.db_service import db_cursor

def _fetchone_dict(cursor):
    row = cursor.fetchone()

    if row is None:
        return None

    if isinstance(row, dict):
        return row

    columns = [
        column[0]
        for column in cursor.description
    ]

    return dict(
        zip(columns, row)
    )

def clean_username(username):
    return str(username).strip()

def clean_email(email):
    return str(email).strip().lower()

def validate_username(username):
    username = clean_username(username)

    if len(username) < 3:
        return (
            False,
            "Username must contain at least 3 characters."
        )

    if len(username) > 50:
        return (
            False,
            "Username must not exceed 50 characters."
        )

    if not re.match(
        r"^[A-Za-z0-9_.-]+$",
        username
    ):
        return (
            False,
            "Username can only contain letters, numbers, "
            "underscores, dots, and hyphens."
        )

    return True, ""

def validate_email(email):
    email = clean_email(email)

    pattern = (
        r"^[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}$"
    )

    if not re.match(
        pattern,
        email
    ):
        return (
            False,
            "Please enter a valid email address."
        )

    return True, ""

def validate_password(password):
    password = str(password)

    if len(password) < 8:
        return (
            False,
            "Password must contain at least 8 characters."
        )

    if not re.search(
        r"[A-Z]",
        password
    ):
        return (
            False,
            "Password must contain at least one uppercase letter."
        )

    if not re.search(
        r"[a-z]",
        password
    ):
        return (
            False,
            "Password must contain at least one lowercase letter."
        )

    if not re.search(
        r"\d",
        password
    ):
        return (
            False,
            "Password must contain at least one number."
        )

    return True, ""

def hash_password(password):
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

def verify_password(
    password,
    password_hash
):
    try:
        if isinstance(
            password_hash,
            bytes
        ):
            password_hash = (
                password_hash.decode(
                    "utf-8"
                )
            )

        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )

    except Exception:
        return False

def username_exists(
    username,
    exclude_user_id=None
):
    username = clean_username(
        username
    )

    try:
        with db_cursor() as cursor:

            if exclude_user_id:
                cursor.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE LOWER(username) = LOWER(%s)
                    AND id != %s
                    LIMIT 1
                    """,
                    (
                        username,
                        exclude_user_id
                    )
                )

            else:
                cursor.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE LOWER(username) = LOWER(%s)
                    LIMIT 1
                    """,
                    (
                        username,
                    )
                )

            return (
                cursor.fetchone()
                is not None
            )

    except Exception as e:
        print(
            "Username check error:",
            e
        )

        return False

def email_exists(
    email,
    exclude_user_id=None
):
    email = clean_email(
        email
    )

    try:
        with db_cursor() as cursor:

            if exclude_user_id:
                cursor.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE LOWER(email) = LOWER(%s)
                    AND id != %s
                    LIMIT 1
                    """,
                    (
                        email,
                        exclude_user_id
                    )
                )

            else:
                cursor.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE LOWER(email) = LOWER(%s)
                    LIMIT 1
                    """,
                    (
                        email,
                    )
                )

            return (
                cursor.fetchone()
                is not None
            )

    except Exception as e:
        print(
            "Email check error:",
            e
        )

        return False

def register_user(
    username,
    email,
    password
):
    username = clean_username(
        username
    )

    email = clean_email(
        email
    )

    valid, message = (
        validate_username(
            username
        )
    )

    if not valid:
        return {
            "success": False,
            "message": message
        }

    valid, message = (
        validate_email(
            email
        )
    )

    if not valid:
        return {
            "success": False,
            "message": message
        }

    valid, message = (
        validate_password(
            password
        )
    )

    if not valid:
        return {
            "success": False,
            "message": message
        }

    if username_exists(
        username
    ):
        return {
            "success": False,
            "message":
                "Username is already in use."
        }

    if email_exists(
        email
    ):
        return {
            "success": False,
            "message":
                "Email is already registered."
        }

    try:
        with db_cursor(
            commit=True
        ) as cursor:

            cursor.execute(
                """
                INSERT INTO users (
                    username,
                    email,
                    password_hash
                )
                VALUES (%s, %s, %s)
                RETURNING
                    id,
                    username,
                    email,
                    created_at
                """,
                (
                    username,
                    email,
                    hash_password(
                        password
                    )
                )
            )

            user = (
                _fetchone_dict(
                    cursor
                )
            )

        return {
            "success": True,
            "message":
                "Account created successfully.",
            "user": user
        }

    except Exception as e:
        print(
            "Registration error:",
            e
        )

        return {
            "success": False,
            "message":
                "Unable to create account."
        }

def authenticate_user(
    email,
    password
):
    email = clean_email(
        email
    )

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    password_hash,
                    created_at,
                    last_login
                FROM users
                WHERE LOWER(email) = LOWER(%s)
                LIMIT 1
                """,
                (
                    email,
                )
            )

            user = (
                _fetchone_dict(
                    cursor
                )
            )

        if not user:
            return {
                "success": False,
                "message":
                    "Invalid email or password."
            }

        if not verify_password(
            password,
            user["password_hash"]
        ):
            return {
                "success": False,
                "message":
                    "Invalid email or password."
            }

        with db_cursor(
            commit=True
        ) as cursor:

            cursor.execute(
                """
                UPDATE users
                SET last_login =
                    CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING
                    id,
                    username,
                    email,
                    created_at,
                    last_login
                """,
                (
                    user["id"],
                )
            )

            updated_user = (
                _fetchone_dict(
                    cursor
                )
            )

        return {
            "success": True,
            "message":
                "Login successful.",
            "user": updated_user
        }

    except Exception as e:
        print(
            "Authentication error:",
            e
        )

        return {
            "success": False,
            "message":
                "Unable to login."
        }

def get_user_by_id(
    user_id
):
    if not user_id:
        return None

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    created_at,
                    last_login
                FROM users
                WHERE id = %s
                LIMIT 1
                """,
                (
                    user_id,
                )
            )

            return _fetchone_dict(
                cursor
            )

    except Exception as e:
        print(
            "Get user error:",
            e
        )

        return None

def get_user_by_email(
    email
):
    email = clean_email(
        email
    )

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    created_at,
                    last_login
                FROM users
                WHERE LOWER(email) = LOWER(%s)
                LIMIT 1
                """,
                (
                    email,
                )
            )

            return _fetchone_dict(
                cursor
            )

    except Exception as e:
        print(
            "Get user by email error:",
            e
        )

        return None

def update_user_profile(
    user_id,
    username,
    email
):
    if not user_id:
        return {
            "success": False,
            "message":
                "Invalid user session."
        }

    username = clean_username(
        username
    )

    email = clean_email(
        email
    )

    valid, message = (
        validate_username(
            username
        )
    )

    if not valid:
        return {
            "success": False,
            "message": message
        }

    valid, message = (
        validate_email(
            email
        )
    )

    if not valid:
        return {
            "success": False,
            "message": message
        }

    if username_exists(
        username,
        user_id
    ):
        return {
            "success": False,
            "message":
                "Username is already in use."
        }

    if email_exists(
        email,
        user_id
    ):
        return {
            "success": False,
            "message":
                "Email is already in use."
        }

    try:
        with db_cursor(
            commit=True
        ) as cursor:

            cursor.execute(
                """
                UPDATE users
                SET
                    username = %s,
                    email = %s
                WHERE id = %s
                RETURNING
                    id,
                    username,
                    email,
                    created_at,
                    last_login
                """,
                (
                    username,
                    email,
                    user_id
                )
            )

            user = (
                _fetchone_dict(
                    cursor
                )
            )

        if not user:
            return {
                "success": False,
                "message":
                    "User account not found."
            }

        return {
            "success": True,
            "message":
                "Profile updated successfully.",
            "user": user
        }

    except Exception as e:
        print(
            "Update profile error:",
            e
        )

        return {
            "success": False,
            "message":
                "Unable to update profile."
        }

def change_password(
    user_id,
    current_password,
    new_password,
    confirm_password
):
    if not user_id:
        return {
            "success": False,
            "message":
                "Invalid user session."
        }

    if not current_password:
        return {
            "success": False,
            "message":
                "Please enter your current password."
        }

    if new_password != confirm_password:
        return {
            "success": False,
            "message":
                "New passwords do not match."
        }

    valid, message = (
        validate_password(
            new_password
        )
    )

    if not valid:
        return {
            "success": False,
            "message": message
        }

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT password_hash
                FROM users
                WHERE id = %s
                LIMIT 1
                """,
                (
                    user_id,
                )
            )

            user = (
                _fetchone_dict(
                    cursor
                )
            )

        if not user:
            return {
                "success": False,
                "message":
                    "User account not found."
            }

        if not verify_password(
            current_password,
            user["password_hash"]
        ):
            return {
                "success": False,
                "message":
                    "Current password is incorrect."
            }

        if verify_password(
            new_password,
            user["password_hash"]
        ):
            return {
                "success": False,
                "message":
                    "New password must be different "
                    "from the current password."
            }

        with db_cursor(
            commit=True
        ) as cursor:

            cursor.execute(
                """
                UPDATE users
                SET password_hash = %s
                WHERE id = %s
                """,
                (
                    hash_password(
                        new_password
                    ),
                    user_id
                )
            )

        return {
            "success": True,
            "message":
                "Password changed successfully."
        }

    except Exception as e:
        print(
            "Change password error:",
            e
        )

        return {
            "success": False,
            "message":
                "Unable to change password."
        }

def reset_password_by_email(
    email,
    new_password,
    confirm_password
):
    email = clean_email(
        email
    )

    if new_password != confirm_password:
        return {
            "success": False,
            "message":
                "Passwords do not match."
        }

    valid, message = (
        validate_password(
            new_password
        )
    )

    if not valid:
        return {
            "success": False,
            "message": message
        }

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE LOWER(email) = LOWER(%s)
                LIMIT 1
                """,
                (
                    email,
                )
            )

            user = (
                _fetchone_dict(
                    cursor
                )
            )

        if not user:
            return {
                "success": False,
                "message":
                    "Account not found."
            }

        with db_cursor(
            commit=True
        ) as cursor:

            cursor.execute(
                """
                UPDATE users
                SET password_hash = %s
                WHERE id = %s
                """,
                (
                    hash_password(
                        new_password
                    ),
                    user["id"]
                )
            )

        return {
            "success": True,
            "message":
                "Password reset successfully."
        }

    except Exception as e:
        print(
            "Reset password error:",
            e
        )

        return {
            "success": False,
            "message":
                "Unable to reset password."
        }