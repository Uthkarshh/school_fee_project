import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        dbname="school_fee_db",
        user="uthkarsh",
        password="Ruthwik081@"
    )

