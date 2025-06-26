from django.shortcuts import render, redirect
from django.db import connection
from datetime import datetime

from core.utils import format_date_for_display


# View to handle "/arbiter" page
def arbiter(request):
    # Get the user name and type from the cookie
    username = request.COOKIES.get("username")
    user_type = request.COOKIES.get("user_type")

    # Get the error and the message info from the URL query parameter
    error = request.GET.get("error")
    message = request.GET.get("message")

    # Check if user is logged in and is an arbiter
    if not username or user_type != "arbiter":
        return redirect("login")

    # Get all matches assigned to this arbiter
    matches = get_arbiter_matches(username)

    # Get rating statistics
    average_rating, total_rated_matches = get_rating_statistics(username)

    context = {
        "matches": matches,
        "average_rating": average_rating,
        "total_rated_matches": total_rated_matches,
        "error": error,
        "message": message,
    }

    # Handle form submissions based on the form_type parameter by calling corresponding function
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "submit_rating":
            return handle_submit_rating(request)
        elif form_type == "submit_result":
            return handle_submit_result(request)

    return render(request, "core/arbiter.html", context)


# Function to get all matches assigned to this arbiter
def get_arbiter_matches(username):
    matches = []
    current_date = datetime.now().strftime("%Y-%m-%d")

    try:
        with connection.cursor() as cursor:
            # Get all matches assigned to this arbiter
            cursor.execute(
                """
                SELECT m.match_id, m.date, m.time_slot, h.hall_name, m.table_id, 
                       t1.team_name as team1_name, t2.team_name as team2_name,
                       m.white_player, m.black_player, m.result, m.ratings
                FROM Matches m
                JOIN Halls h ON m.hall_id = h.hall_id
                JOIN Teams t1 ON m.team1_id = t1.team_id
                JOIN Teams t2 ON m.team2_id = t2.team_id
                WHERE m.arbiter_username = %s
                ORDER BY m.date DESC, m.time_slot
            """,
                [username],
            )
            rows = cursor.fetchall()

            for row in rows:
                match_date = row[1]
                is_past_match = str(match_date) <= current_date

                formatted_date = format_date_for_display(match_date)

                match_data = {
                    "match_id": row[0],
                    "date": formatted_date,
                    "time_slot": row[2],
                    "hall_name": row[3],
                    "table_id": row[4],
                    "team1_name": row[5],
                    "team2_name": row[6],
                    "white_player": row[7],
                    "black_player": row[8],
                    "result": row[9],
                    "ratings": row[10],
                    "is_future": not is_past_match,
                }
                matches.append(match_data)

    except Exception as e:
        print(f"Database error: {e}")

    return matches


# Function to get rating statistics for the arbiter
def get_rating_statistics(username):
    average_rating = None
    total_rated_matches = 0

    try:
        with connection.cursor() as cursor:
            # Get average rating and total rated matches
            cursor.execute(
                """
                SELECT AVG(ratings), COUNT(match_id)
                FROM Matches
                WHERE arbiter_username = %s AND ratings IS NOT NULL
            """,
                [username],
            )

            result = cursor.fetchone()
            if result and result[0] is not None:
                average_rating = round(result[0], 2)
                total_rated_matches = result[1]

    except Exception as e:
        print(f"Database error: {e}")

    return average_rating, total_rated_matches


# Function to handle the form submission for rating a match
def handle_submit_rating(request):
    # Get the match ID, rating, and username from the request
    match_id = request.POST.get("match_id")
    rating = request.POST.get("rating")

    # Get the username from the cookies
    username = request.COOKIES.get("username")

    if not all([match_id, rating, username]):
        return redirect(f"/arbiter?error=Missing required fields")

    try:
        rating = int(rating)
        if not (1 <= rating <= 10):
            return redirect(f"/arbiter?error=Rating must be between 1 and 10")

        # Check if the match can be rated by this arbiter
        with connection.cursor() as cursor:
            # Get the match date and current rating
            cursor.execute(
                """
                SELECT date, ratings
                FROM Matches
                WHERE match_id = %s AND arbiter_username = %s
            """,
                [match_id, username],
            )

            result = cursor.fetchone()
            if not result:
                return redirect(
                    f"/arbiter?error=Match not found or does not belong to this arbiter"
                )

            match_date = result[0]
            current_rating = result[1]
            current_date = datetime.now().date()

            # Check if the match date has passed
            if match_date > current_date:
                return redirect(f"/arbiter?error=Cannot rate a future match")

            # Check if the match is already rated
            if current_rating is not None:
                return redirect(f"/arbiter?error=Match already rated")

            # Submit the rating
            cursor.execute(
                """
                UPDATE Matches
                SET ratings = %s
                WHERE match_id = %s
            """,
                [rating, match_id],
            )

            return redirect(f"/arbiter?message=Rating submitted successfully")

    except ValueError:
        return redirect(f"/arbiter?error=Invalid rating value")
    except Exception as e:
        print(f"Database error: {e}")
        return redirect(f"/arbiter?error=Failed to submit rating: {e}")

    return redirect("arbiter")


# Function to handle the form submission for match result
def handle_submit_result(request):
    match_id = request.POST.get("match_id")
    result = request.POST.get("result")
    username = request.COOKIES.get("username")

    if not all([match_id, result, username]):
        return redirect(f"/arbiter?error=Missing required fields")

    try:
        # Validate result value
        valid_results = ["white wins", "black wins", "draw"]
        if result not in valid_results:
            return redirect(f"/arbiter?error=Invalid result value")

        # Check if the match can be rated by this arbiter
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT date, result
                FROM Matches
                WHERE match_id = %s AND arbiter_username = %s
            """,
                [match_id, username],
            )

            match_info = cursor.fetchone()
            if not match_info:
                return redirect(
                    f"/arbiter?error=Match not found or does not belong to this arbiter"
                )

            match_date = match_info[0]
            current_result = match_info[1]
            current_date = datetime.now().date()

            # Check if the match date has passed
            if match_date > current_date:
                return redirect(
                    f"/arbiter?error=Cannot decide result for a future match"
                )

            # Check if the match result is already set
            if current_result is not None:
                return redirect(f"/arbiter?error=Match result already decided")

            # Submit the result
            cursor.execute(
                """
                UPDATE Matches
                SET result = %s
                WHERE match_id = %s
            """,
                [result, match_id],
            )

            return redirect(f"/arbiter?message=Match result submitted successfully")

    except Exception as e:
        print(f"Database error: {e}")
        return redirect(f"/arbiter?error=Failed to submit match result: {e}")

    return redirect("arbiter")
