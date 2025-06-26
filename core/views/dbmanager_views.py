from django.shortcuts import render, redirect
from django.db import connection
import re

from core.utils import hash_password, get_all_halls, format_date_for_db


# View to handle "/dbmanager" page
def dbmanager(request):
    # Get the username from the cookie
    username = request.COOKIES.get("username")
    user_type = request.COOKIES.get("user_type")

    # Check if user is logged in and is a database manager
    if not username or user_type != "dbmanager":
        return redirect("login")

    halls = get_all_halls()

    # Get the error and the message info from the URL query parameter
    error = request.GET.get("error")
    message = request.GET.get("message")
    context = {"halls": halls, "error": error, "message": message}

    # Handle form submissions based on the form_type parameter by calling corresponding function
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "add_user_player":
            return handle_add_user_player(request)
        elif form_type == "add_user_coach":
            return handle_add_user_coach(request)
        elif form_type == "add_user_arbiter":
            return handle_add_user_arbiter(request)
        elif form_type == "rename_hall":
            return handle_rename_hall(request)

    return render(request, "core/dbmanager.html", context)


# Function to handle adding a new player
def handle_add_user_player(request):
    # Get the form data from the reques
    username = request.POST.get("username")
    password = request.POST.get("password")
    name = request.POST.get("name")
    surname = request.POST.get("surname")
    nationality = request.POST.get("nationality")
    date_of_birth = request.POST.get("date_of_birth")
    fide_id = request.POST.get("fide_id")
    elo_rating_str = request.POST.get("elo_rating")
    title = request.POST.get("title")

    # Validate password
    is_valid, error_message = validate_password(password)
    if not is_valid:
        return redirect(f"/dbmanager?error={error_message}")

    db_date_of_birth = format_date_for_db(date_of_birth)

    # Convert elo_rating to integer
    elo_rating = None
    if elo_rating_str and elo_rating_str.isdigit():
        elo_rating = int(elo_rating_str)

    # Hash the password for security
    hashed_password = hash_password(password)

    try:
        with connection.cursor() as cursor:
            # Insert the new player into the Players table
            sql = """
            INSERT INTO Players (username, password, name, surname, nationality, date_of_birth, fide_id, elo_rating, title)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                sql,
                [
                    username,
                    hashed_password,
                    name,
                    surname,
                    nationality,
                    db_date_of_birth,
                    fide_id,
                    elo_rating,
                    title,
                ],
            )

        return redirect(f"/dbmanager?message=Player added successfully!")

    except Exception as e:
        return redirect(f"/dbmanager?error=Failed to add player: {e}")


# Function to handle adding a new coach
def handle_add_user_coach(request):
    # Get the form data from the request
    username = request.POST.get("username")
    password = request.POST.get("password")
    name = request.POST.get("name")
    surname = request.POST.get("surname")
    nationality = request.POST.get("nationality")
    team_ID = request.POST.get("coach_team")
    contract_start_date = request.POST.get("contract_start_date")
    contract_finish_date = request.POST.get("contract_finish_date")

    # Validate password
    is_valid, error_message = validate_password(password)
    if not is_valid:
        return redirect(f"/dbmanager?error={error_message}")

    # Hash the password for security
    hashed_password = hash_password(password)

    try:
        with connection.cursor() as cursor:
            # Insert the new coach into the Coaches table
            sql = """
            INSERT INTO Coaches (username, password, name, surname, nationality)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, [username, hashed_password, name, surname, nationality])

            # Insert the coach's team and contract details into the CoachTeams table
            sql2 = """
            INSERT INTO CoachTeams (username, team_id, contract_start, contract_finish) 
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(
                sql2,
                [
                    username,
                    team_ID,
                    format_date_for_db(contract_start_date),
                    format_date_for_db(contract_finish_date),
                ],
            )
        return redirect(f"/dbmanager?message=Coach added successfully!")

    except Exception as e:
        print(e)
        return redirect(f"/dbmanager?error=Failed to add coach: {e}")


# Function to handle adding a new arbiter
def handle_add_user_arbiter(request):
    # Get the form data from the request
    username = request.POST.get("username")
    password = request.POST.get("password")
    name = request.POST.get("name")
    surname = request.POST.get("surname")
    nationality = request.POST.get("nationality")
    experience_level = request.POST.get("experience_level")

    # Validate password
    is_valid, error_message = validate_password(password)
    if not is_valid:
        return redirect(f"/dbmanager?error={error_message}")

    # Hash the password for security
    hashed_password = hash_password(password)

    try:
        with connection.cursor() as cursor:
            # Insert the new arbiter into the Arbiters table
            sql = """
            INSERT INTO Arbiters (username, password, name, surname, nationality, experience_level)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                sql,
                [
                    username,
                    hashed_password,
                    name,
                    surname,
                    nationality,
                    experience_level,
                ],
            )
        return redirect(f"/dbmanager?message=Arbiter added successfully!")

    except Exception as e:
        return redirect(f"/dbmanager?error=Failed to add arbiter: {e}")


# Function to handle renaming a hall
def handle_rename_hall(request):
    # Get the form data from the request
    hall_id = request.POST.get("hall_id")
    new_name = request.POST.get("new_name")

    try:
        with connection.cursor() as cursor:
            # Update the hall name in the Halls table
            sql = "UPDATE Halls SET hall_name = %s WHERE hall_id = %s"
            cursor.execute(sql, [new_name, hall_id])

            # Check if the update was successful
            if cursor.rowcount == 0:
                return redirect(f"/dbmanager?error=Hall not found or no changes made.")

        return redirect(f"/dbmanager?message=Hall renamed successfully!")

    except Exception as e:
        return redirect(f"/dbmanager?error=Failed to rename hall: {e}")


# Function to validate the password
def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must include at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must include at least one lowercase letter"

    if not re.search(r"[0-9]", password):
        return False, "Password must include at least one digit"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must include at least one special character"

    return True, ""
