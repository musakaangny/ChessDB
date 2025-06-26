from django.shortcuts import render, redirect
from django.db import connection


# View to handle "/player" page
def player(request):
    # Get the username from the cookie
    username = request.COOKIES.get("username")
    user_type = request.COOKIES.get("user_type")

    # Get the error and message from the URL parameters of the request
    error = request.GET.get("error")
    message = request.GET.get("message")

    # Check if user is logged in and is a player
    if not username or user_type != "player":
        return redirect("login")

    # Get the necessary data for the player page
    players = get_all_player_played_against(username)
    most_played_info = get_most_played_rating(username)
    context = {
        "players": players,
        "most_played_info": most_played_info,
        "error": error,
        "message": message,
    }

    return render(request, "core/player.html", context)


# Function to get all players the user has played against
def get_all_player_played_against(username):
    players = []

    try:
        with connection.cursor() as cursor:
            # Fetch all players the user has played against (use DISTINCT to avoid duplicates)
            cursor.execute(
                """SELECT DISTINCT P.name, P.surname 
                           FROM Players P, Matches M 
                           WHERE ((M.white_player = %s AND M.black_player = P.username)
                           OR 
                           (M.black_player = %s AND M.white_player = P.username))
                           AND
                           M.date < CURDATE()""",
                [username, username],
            )
            players = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching players played against: {e}")

    return players


# Function to get the most played opponent and their rating
def get_most_played_rating(username):
    most_played_info = {"match_count": 0, "is_tie": False, "elo_rating": None}

    try:
        with connection.cursor() as cursor:
            # Fetch the most played opponent and their match count
            cursor.execute(
                """
                SELECT opponent_username, COUNT(*) as match_count
                FROM (
                    SELECT IF(white_player = %s, black_player, white_player) as opponent_username
                    FROM Matches
                    WHERE (white_player = %s OR black_player = %s) AND date < CURDATE()
                ) as Opponents
                GROUP BY opponent_username
                ORDER BY match_count DESC
            """,
                [username, username, username],
            )

            match_counts = cursor.fetchall()

            # If no matches found
            if not match_counts:
                return most_played_info

            max_count = match_counts[0][1]
            most_played_info["match_count"] = max_count

            # Get all players with the max count (could be multiple if tied)
            most_played_opponents = [
                opponent for opponent, count in match_counts if count == max_count
            ]

            if len(most_played_opponents) == 1:
                # Only one player with max count
                most_played_info["is_tie"] = False

                # Fetch the elo rating of the most played opponent
                cursor.execute(
                    """
                    SELECT elo_rating
                    FROM Players
                    WHERE username = %s
                """,
                    [most_played_opponents[0]],
                )

                result = cursor.fetchone()

                if result:
                    most_played_info["elo_rating"] = result[0]
            else:
                # Multiple players tied for max count
                most_played_info["is_tie"] = True
                placeholders = ", ".join(["%s"] * len(most_played_opponents))

                # Fetch the average elo rating of the tied players
                sql = f"""
                    SELECT AVG(elo_rating)
                    FROM Players
                    WHERE username IN ({placeholders})
                """
                cursor.execute(sql, most_played_opponents)

                result = cursor.fetchone()

                if result:
                    most_played_info["elo_rating"] = result[0]

    except Exception as e:
        print(f"Error fetching most played rating: {e}")

    return most_played_info
