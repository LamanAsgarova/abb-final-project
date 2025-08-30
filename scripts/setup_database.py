import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.services.database_service import init_db, add_user

def main():
    # Initialize the database and table
    init_db()

    # Add users
    users_to_add = [
        {"username": "admin", "password": "adminpassword", "role": "Admin"},
        {"username": "data_user", "password": "password1", "role": "Data Tribe"},
        {"username": "mobile_user", "password": "password2", "role": "Mobile Application Tribe"},
        {"username": "risk_user", "password": "password3", "role": "Risk Tribe"},
        {"username": "card_user", "password": "password4", "role": "Card Tribe"}
    ]

    for user in users_to_add:
        add_user(user["username"], user["password"], user["role"])

if __name__ == "__main__":
    main()