from django.db import connection
import hashlib
from datetime import datetime


# Function to hash passwords using SHA-256 algorithm
def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# Function to format dates for display in the desired format, YYYY-MM-DD to DD-MM-YYYY
def format_date_for_display(date_string):
    if not date_string:
        return None

    try:
        if isinstance(date_string, datetime) or hasattr(date_string, "strftime"):
            return date_string.strftime("%d-%m-%Y")
        # Parse the input date string (assuming it is in YYYY-MM-DD format)
        dt = datetime.strptime(str(date_string), "%Y-%m-%d")
        # Format to DD-MM-YYYY
        return dt.strftime("%d-%m-%Y")

    except (ValueError, TypeError):
        return date_string


# Function to format dates for proper database storage, DD-MM-YYYY to YYYY-MM-DD
def format_date_for_db(date_string):
    if not date_string:
        return None

    try:
        # Parse the input date string (assuming it's in DD-MM-YYYY format)
        dt = datetime.strptime(str(date_string), "%d-%m-%Y")
        # Format to YYYY-MM-DD
        return dt.strftime("%Y-%m-%d")

    except (ValueError, TypeError):
        # If it's already in YYYY-MM-DD format, try to parse and return it
        try:
            dt = datetime.strptime(str(date_string), "%Y-%m-%d")
            return str(date_string)

        except (ValueError, TypeError):
            return date_string


# Function to fetch all halls from the database
# This function is in the utils.py file because it is used in multiple views
def get_all_halls():
    halls = []

    try:
        with connection.cursor() as cursor:
            # Fetch all halls from the Halls table
            cursor.execute(
                "SELECT hall_id, hall_name, country, capacity FROM Halls ORDER BY hall_name"
            )
            halls = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching halls: {e}")

    return halls
