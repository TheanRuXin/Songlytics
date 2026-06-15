import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="songlytics",
        user="postgres",
        password="r2u0x0i5n",
        port="5432"
    )