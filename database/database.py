# database.py
import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="songlytics",
        user="postgres",
        password="r2u0x0i5n",
        port="5432"
    )
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        age INTEGER,
        gender VARCHAR(20),
        biography TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. 预测历史表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prediction_history (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        song_name VARCHAR(255),
        prediction VARCHAR(50),
        probability DOUBLE PRECISION,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS simulation_history (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        song_name VARCHAR(255),
        original_score DOUBLE PRECISION,
        new_score DOUBLE PRECISION,
        changes JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 3 tables created successfully!")

if __name__ == "__main__":
    try:
        create_tables()
        print("Database setup complete!")
    except Exception as e:
        print(f"Error: {e}")