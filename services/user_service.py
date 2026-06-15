import psycopg2
import bcrypt
from datetime import datetime

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="songlytics",
        user="postgres",
        password="r2u0x0i5n",
        port="5432"
    )

def hash_password(password):
    salt = bcrypt.gensalt(rounds=12) 
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def get_user_by_id(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, created_at FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "created_at": user[3]
            }
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def get_user_by_email(email):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash, created_at FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "password_hash": user[3],
                "created_at": user[4]
            }
        return None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

def update_user_profile(user_id, username=None, email=None, password=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if username:
            updates.append("username = %s")
            params.append(username)
        
        if email:
            updates.append("email = %s")
            params.append(email)
        
        if password:
            hashed = hash_password(password)
            updates.append("password_hash = %s")
            params.append(hashed)
        
        if not updates:
            return False
        
        updates.append("updated_at = %s")
        params.append(datetime.now())
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, params)
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False

def authenticate_user(email, password):
    try:
        user = get_user_by_email(email)
        
        if not user:
            return None
        
        if verify_password(password, user["password_hash"]):
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }
        return None
    except Exception as e:
        print(f"Error authenticating: {e}")
        return None

def register_user(username, email, password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return None, "Email already exists"

        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return None, "Username already exists"
        
        hashed_password = hash_password(password)
        
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (username, email, hashed_password, datetime.now(), datetime.now()))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return user_id, "Success"
    except Exception as e:
        print(f"Error registering user: {e}")
        return None, str(e)

def change_password(user_id, old_password, new_password):
    try:
        user = get_user_by_id(user_id)
        if not user:
            return False, "User not found"
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
        current_hash = cursor.fetchone()[0]
        
        if not verify_password(old_password, current_hash):
            cursor.close()
            conn.close()
            return False, "Current password is incorrect"
        
        new_hashed = hash_password(new_password)
        cursor.execute(
            "UPDATE users SET password_hash = %s, updated_at = %s WHERE id = %s",
            (new_hashed, datetime.now(), user_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Password changed successfully"
    except Exception as e:
        print(f"Error changing password: {e}")
        return False, str(e)

def delete_user_account(user_id, password):
    try:
        user = get_user_by_id(user_id)
        if not user:
            return False, "User not found"
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
        current_hash = cursor.fetchone()[0]
        
        if not verify_password(password, current_hash):
            cursor.close()
            conn.close()
            return False, "Password is incorrect"
        
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Account deleted successfully"
    except Exception as e:
        print(f"Error deleting account: {e}")
        return False, str(e)

def get_user_stats(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()      
        
        cursor.execute("SELECT COUNT(*) FROM prediction_history WHERE user_id = %s", (user_id,))
        total_predictions = cursor.fetchone()[0]       
        
        cursor.execute("SELECT COUNT(*) FROM simulation_history WHERE user_id = %s", (user_id,))
        total_simulations = cursor.fetchone()[0]
        
        cursor.execute(
            "SELECT COUNT(*) FROM prediction_history WHERE user_id = %s AND prediction = 'High Popularity'",
            (user_id,)
        )
        high_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "total_predictions": total_predictions,
            "total_simulations": total_simulations,
            "high_count": high_count,
            "high_rate": (high_count / total_predictions * 100) if total_predictions > 0 else 0
        }
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return {
            "total_predictions": 0,
            "total_simulations": 0,
            "high_count": 0,
            "high_rate": 0
        }