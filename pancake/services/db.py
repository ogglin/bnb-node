import time

import psycopg2

import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

from config import *


def _query(q):
    # print(q)
    cur = None
    # while cur == None:
    try:
        con = psycopg2.connect(
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT
        )
        cur = con.cursor()
    except Exception as exc:
        print(exc)
        time.sleep(3)
    try:
        cur.execute(q)
        data = cur.fetchall()
    except psycopg2.DatabaseError as err:
        if 'no results' not in str(err):
            print("Error: ", err)
        print("Error: ", err)
    else:
        return data
    finally:
        con.commit()
