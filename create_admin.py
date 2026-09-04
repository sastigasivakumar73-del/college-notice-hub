"""
create_admin.py
----------------
Run this ONCE to create the first admin account for College Notice Hub.

Usage:
    python create_admin.py

It will ask you to type a username and password in the terminal.
The password is hashed before being stored - it is never saved as plain text.
"""

import sqlite3
import getpass
from werkzeug.security import generate_password_hash

from app import init_db, DATABASE


def create_admin():
    # Make sure the tables exist before we try to insert into them.
    init_db()

    print("=== Create College Notice Hub Admin Account ===")
    username = input("Enter admin username: ").strip()
    password = getpass.getpass("Enter admin password: ")
    confirm_password = getpass.getpass("Confirm admin password: ")

    if not username or not password:
        print("Username and password cannot be empty.")
        return

    if password != confirm_password:
        print("Passwords do not match. Please try again.")
        return

    password_hash = generate_password_hash(password)

    db = sqlite3.connect(DATABASE)
    try:
        db.execute(
            "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        db.commit()
        print(f"\nAdmin account '{username}' created successfully!")
        print("You can now log in at /admin/login")
    except sqlite3.IntegrityError:
        print(f"\nAn admin with username '{username}' already exists.")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
