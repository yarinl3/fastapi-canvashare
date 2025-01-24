import os
from fastapi import HTTPException, status
import psycopg2
import urllib.parse as urlparse

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

def is_safe_remove_photo(photo_name: str):
    con, cur = connect_to_db()
    photo_name = f'%{photo_name}'
    results = []
    cur.execute("SELECT * FROM users WHERE profile_photo LIKE %s OR cover_photo LIKE %s", (photo_name, photo_name))
    results += cur.fetchall()
    cur.execute("SELECT * FROM paints WHERE photo LIKE %s", (photo_name, ))
    results += cur.fetchall()
    con.close()
    if len(results) < 2:
        return True
    return False
