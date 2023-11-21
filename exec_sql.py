import psycopg2
import dotenv
import os

dotenv.load_dotenv()

USERNAME = os.getenv('DBUSERNAME')
PASSWORD = os.getenv('DBPASSWORD')


def get_connection():
    try:
        return psycopg2.connect(
            database=USERNAME,
            user=USERNAME,
            password=PASSWORD,
            host="bubble.db.elephantsql.com",
            port=5432,
        )
    except Exception as e:
        print(e)
        return False


conn = get_connection()

curr = conn.cursor()

sql = open('main.sql', 'r').read()

curr.execute(sql)

conn.commit()

curr.close()

conn.close()