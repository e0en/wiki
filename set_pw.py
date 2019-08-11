#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
from bcrypt import gensalt, hashpw, checkpw

from secret import DATABASE


def main():
    pw = input('New password:')
    salt = gensalt()
    pw_hash = hashpw(pw.encode('utf-8'), salt)

    salt = salt.decode('utf-8')
    pw_hash = pw_hash.decode('utf-8')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE users SET hashed_pw=?, salt=?", (pw_hash, salt))
    conn.commit()
    c.execute(f"SELECT * from users")
    print(c.fetchone())
    conn.close()


if __name__ == "__main__":
    main()
