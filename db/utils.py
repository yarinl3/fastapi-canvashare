import os
from dotenv import load_dotenv
from fastapi import HTTPException, status
import urllib.parse as urlparse
import psycopg2

load_dotenv()
url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

def connect_to_db() -> tuple:
    con = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cur = con.cursor()
    return con, cur

def commit_and_close_db(con) -> None:
    con.commit()
    con.close()

def raise_error_if_guest(user_id: int | None) -> None:
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

def raise_error_if_blocked(user_id: int | None) -> None:
    if user_id is None:
        return # If the user is guest do not raise error
    con, cur = connect_to_db()
    cur.execute("SELECT * FROM users WHERE id = %s AND is_blocked=False", (user_id,))
    if not cur.fetchall():
        con.close()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is blocked")
    con.close()
