import re
import bcrypt

from services.db_service import db_cursor

def clean_username(username):
    return username.strip()

def clean_email(email):
    return email.strip().lower()

def validate_username(username):
    username = clean_username(username)

    if len(username) < 3:
        return False, "Username must contain at least 3 characters."

    if len(username) > 50:
        return False, "Username must not exceed 50 characters."

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", username):
        return False, (
            "Username can only contain letters, numbers, "
            "underscore, dot and hyphen."
        )

    return True, None

def validate_email(email):
    email = clean_email(email)

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.fullmatch(pattern, email):
        return False, "Please enter a valid email address."

    return True, None

def validate_password(password):
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."

    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter."

    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number."

    return True, None

def hash_password(password):
    password_bytes = password.encode("utf-8")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")

def verify_password(password, password_hash):
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )

    except Exception:
        return False

def username_exists(username):
    username = clean_username(username)

    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM users
            WHERE LOWER(username) = LOWER(%s)
            LIMIT 1
            """,
            (username,)
        )

        return cursor.fetchone() is not None

def email_exists(email):
    email = clean_email(email)

    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM users
            WHERE LOWER(email) = LOWER(%s)
            LIMIT 1
            """,
            (email,)
        )

        return cursor.fetchone() is not None

def register_user(username, email, password):
    username = clean_username(username)
    email = clean_email(email)

    valid, message = validate_username(username)

    if not valid:
        return {
            "success": False,
            "message": message
        }

    valid, message = validate_email(email)

    if not valid:
        return {
            "success": False,
            "message": message
        }

    valid, message = validate_password(password)

    if not valid:
        return {
            "success": False,
            "message": message
        }

    if username_exists(username):
        return {
            "success": False,
            "message": "Username is already registered."
        }

    if email_exists(email):
        return {
            "success": False,
            "message": "Email is already registered."
        }

    password_hash = hash_password(password)

    try:
        with db_cursor(commit=True) as cursor:
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
                    password_hash
                )
            )

            row = cursor.fetchone()

        return {
            "success": True,
            "message": "Account created successfully.",
            "user": {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "created_at": row[3]
            }
        }

    except Exception as e:
        print("Register error:", e)

        return {
            "success": False,
            "message": "Unable to create account."
        }

def authenticate_user(identifier, password):
    identifier = identifier.strip()

    if not identifier or not password:
        return {
            "success": False,
            "message": "Please enter your username/email and password."
        }

    try:
        with db_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    username,
                    email,
                    password_hash,
                    created_at
                FROM users
                WHERE
                    LOWER(username) = LOWER(%s)
                    OR LOWER(email) = LOWER(%s)
                LIMIT 1
                """,
                (
                    identifier,
                    identifier
                )
            )

            row = cursor.fetchone()

        if row is None:
            return {
                "success": False,
                "message": "Invalid username/email or password."
            }

        user_id = row[0]
        username = row[1]
        email = row[2]
        password_hash = row[3]
        created_at = row[4]

        if not verify_password(
            password,
            password_hash
        ):
            return {
                "success": False,
                "message": "Invalid username/email or password."
            }

        with db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                UPDATE users
                SET last_login = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (user_id,)
            )

        return {
            "success": True,
            "message": "Login successful.",
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "created_at": created_at
            }
        }

    except Exception as e:
        print("Login error:", e)

        return {
            "success": False,
            "message": "Unable to log in."
        }

def get_user_by_id(user_id):
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
                (user_id,)
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "created_at": row[3],
            "last_login": row[4]
        }

    except Exception as e:
        print("Get user error:", e)
        return None