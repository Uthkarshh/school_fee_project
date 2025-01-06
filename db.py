import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        dbname="school_fee_db",
        user="username",
        password="password@"
    )

