from django.shortcuts import render, redirect
from django.db import connection
from django.http import JsonResponse

from core.utils import get_all_halls, format_date_for_db, format_date_for_display


# View to handle "/coach" page
def coach(request):
    # Get the username from the cookie
    username = request.COOKIES.get("username")
    user_type = request.COOKIES.get("user_type")

    # Check if user is logged in and is a coach
    if not username or user_type != "coach":
        return redirect("login")

    # Handle GET requests with action parameter by calling corresponding function
    if request.method == "GET" and "action" in request.GET:
        action = request.GET.get("action")

        if action == "get_available_tables":
            return get_available_tables(request)
        elif action == "get_available_arbiters":
            return get_available_arbiters(request)
        elif action == "get_available_team_players":
            return get_available_team_players(request)
        elif action == "get_available_players_for_team":
            return get_available_players_for_team(request)

    context = get_context_data(username)  # Get context data for the coach view

    # Get the error and message info from the URL query parameter and add to context
    context["error"] = request.GET.get("error")
    context["message"] = request.GET.get("message")

    # Handle form submissions based on the form_type parameter by calling corresponding function
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "create_match":
            return handle_create_match(request)
        elif form_type == "delete_match":
            return handle_delete_match(request)
        elif form_type == "assign_player":
            return handle_assign_player(request)
        elif form_type == "assign_player":
            return handle_assign_player(request)

    return render(request, "core/coach.html", context)


# Function to get all available tables for a given hall, date, and time slot
def get_available_tables(request):
    # Get hall_id, date, and time_slot from the request
    hall_id = request.GET.get("hall_id")
    date = request.GET.get("date")
    db_date = format_date_for_db(date)
    time_slot = request.GET.get("time_slot")

    tables = []
    try:
        with connection.cursor() as cursor:
            # Get available tables for the selected date and time slot in the selected hall
            cursor.execute(
                """
                SELECT t.table_id, t.table_id
                FROM Tables t
                WHERE t.hall_id = %s
                AND t.table_id NOT IN (
                    SELECT m.table_id
                    FROM Matches m
                    WHERE m.date = %s AND m.time_slot = %s
                )
                ORDER BY t.table_id
            """,
                [hall_id, db_date, time_slot],
            )
            tables = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching tables: {e}")

    return JsonResponse(list(tables), safe=False)


# Function to get all available arbiters for a given date and time slot
def get_available_arbiters(request):
    # Get date and time_slot from the request
    date = request.GET.get("date")
    db_date = format_date_for_db(date)
    time_slot = request.GET.get("time_slot")

    arbiters = []
    try:
        with connection.cursor() as cursor:
            # Get available arbiters for the selected date and time slot
            cursor.execute(
                """
                SELECT a.username, CONCAT(a.name, ' ', a.surname, ' (', a.experience_level, ')')
                FROM Arbiters a
                WHERE a.username NOT IN (
                    SELECT m.arbiter_username
                    FROM Matches m
                    WHERE m.date = %s AND m.time_slot = %s
                )
                ORDER BY a.name, a.surname
            """,
                [db_date, time_slot],
            )
            arbiters = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching arbiters: {e}")

    return JsonResponse(list(arbiters), safe=False)


# Function to get all available players for a given team, date, and time slot
def get_available_team_players(request):
    # Get team_id, date, and time_slot from the request
    team_id = request.GET.get("team_id")
    date = request.GET.get("date")
    db_date = format_date_for_db(date)
    time_slot = request.GET.get("time_slot")

    players = []
    try:
        with connection.cursor() as cursor:
            # Get available players for the selected date and time slot in the selected team
            cursor.execute(
                """
                SELECT p.username, CONCAT(p.name, ' ', p.surname, ' (', p.title, ', ', p.elo_rating, ')')
                FROM Players p
                JOIN PlayerTeams pt ON p.username = pt.username
                WHERE pt.team_id = %s
                AND p.username NOT IN (
                    SELECT m.white_player
                    FROM Matches m
                    WHERE m.date = %s AND m.time_slot = %s AND m.white_player IS NOT NULL
                    UNION
                    SELECT m.black_player
                    FROM Matches m
                    WHERE m.date = %s AND m.time_slot = %s AND m.black_player IS NOT NULL
                )
                ORDER BY p.name, p.surname
            """,
                [team_id, db_date, time_slot, db_date, time_slot],
            )
            players = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching players: {e}")

    return JsonResponse(list(players), safe=False)


# Function to get the coach's team
def get_coach_team(username):
    team = None
    try:
        with connection.cursor() as cursor:
            # Get the team coached by the current coach
            cursor.execute(
                """
                SELECT t.team_id, t.team_name
                FROM Teams t
                JOIN CoachTeams ct ON t.team_id = ct.team_id
                WHERE ct.username = %s
                AND CURRENT_DATE BETWEEN ct.contract_start AND ct.contract_finish
                ORDER BY t.team_name
            """,
                [username],
            )
            team = cursor.fetchone()
    except Exception as e:
        print(f"Error fetching coach team: {e}")
    return team


# Function to get all opponent teams (teams not coached by the current coach)
def get_opponent_teams(username):
    teams = []
    try:
        with connection.cursor() as cursor:
            # Get all teams except the ones coached by the current coach
            cursor.execute(
                """
                SELECT t.team_id, t.team_name
                FROM Teams t
                WHERE t.team_id NOT IN (
                    SELECT ct.team_id
                    FROM CoachTeams ct
                    WHERE ct.username = %s
                    AND CURRENT_DATE BETWEEN ct.contract_start AND ct.contract_finish
                )
                ORDER BY t.team_name
            """,
                [username],
            )
            teams = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching opponent teams: {e}")
    return teams


# Function to get all matches created by the coach
def get_coach_created_matches(username):
    matches = []
    try:
        with connection.cursor() as cursor:
            # Get matches created by the coach (where coach_username matches)
            cursor.execute(
                """
                SELECT m.match_id, m.date, m.time_slot,
                       h.hall_name, t.table_id,
                       t1.team_name AS team1_name, t2.team_name AS team2_name,
                       CONCAT(p1.name, ' ', p1.surname) AS white_player_name,
                       CONCAT(p2.name, ' ', p2.surname) AS black_player_name,
                       CONCAT(a.name, ' ', a.surname) AS arbiter_name,
                       m.result
                FROM Matches m
                JOIN Halls h ON m.hall_id = h.hall_id
                JOIN Tables t ON m.table_id = t.table_id
                JOIN Teams t1 ON m.team1_id = t1.team_id
                JOIN Teams t2 ON m.team2_id = t2.team_id
                JOIN Players p1 ON m.white_player = p1.username
                LEFT JOIN Players p2 ON m.black_player = p2.username
                JOIN Arbiters a ON m.arbiter_username = a.username
                WHERE m.coach_username = %s
                ORDER BY m.date DESC, m.time_slot
            """,
                [username],
            )
            rows = cursor.fetchall()

            for row in rows:
                formatted_match = list(row)
                formatted_match[1] = format_date_for_display(row[1])
                matches.append(formatted_match)
    except Exception as e:
        print(f"Error fetching coach created matches: {e}")
    return matches


# Function to handle the creation of a new match
def handle_create_match(request):
    try:
        # Get match details from the request
        date = request.POST.get("date")
        db_date = format_date_for_db(date)
        time_slot = request.POST.get("time_slot")
        hall_id = request.POST.get("hall_id")
        table_id = request.POST.get("table_id")
        team_id = request.POST.get("team_id")  # Coach's team
        opponent_team_id = request.POST.get("opponent_team_id")
        arbiter_username = request.POST.get("arbiter_username")
        player_username = request.POST.get("player_username")

        # Get the coach's username from the cookies
        coach_username = request.COOKIES.get("username")

        # We can safely assume that the coach's team is the white team (team1)
        team1_id = team_id
        team2_id = opponent_team_id

        # Same as above, we can assume that the player is the white player
        white_player = player_username

        with connection.cursor() as cursor:
            # Insert the match in the database
            cursor.execute(
                """
                INSERT INTO Matches (date, time_slot, hall_id, table_id, team1_id, team2_id, 
                                    arbiter_username, white_player, black_player, coach_username)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)            """,
                [
                    db_date,
                    time_slot,
                    hall_id,
                    table_id,
                    team1_id,
                    team2_id,
                    arbiter_username,
                    white_player,
                    None,
                    coach_username,
                ],
            )

        return redirect("/coach?message=Match created successfully!")

    except Exception as e:
        return redirect(f"/coach?error=Failed to create match: {e}")


# Function to handle the deletion of a match
def handle_delete_match(request):
    try:
        # Get match_id from the request
        match_id = request.POST.get("match_id")

        # Get the coach's username from the cookies
        username = request.COOKIES.get("username")

        with connection.cursor() as cursor:
            # Check if the coach is the creator of the match
            cursor.execute(
                """
                SELECT coach_username FROM Matches 
                WHERE match_id = %s
            """,
                [match_id],
            )
            result = cursor.fetchone()

            if not result or result[0] != username:
                return redirect(
                    "/coach?error=You are not authorized to delete this match."
                )

            # Delete the match
            cursor.execute("DELETE FROM Matches WHERE match_id = %s", [match_id])

        return redirect("/coach?message=Match deleted successfully!")

    except Exception as e:
        return redirect(f"/coach?error=Failed to delete match: {e}")


# Function to handle the assignment of a player to a match
def handle_assign_player(request):
    try:
        # Get match details from the request
        match_id = request.POST.get("match_id")
        player_username = request.POST.get("player_username")

        with connection.cursor() as cursor:
            # Assign the player to the match as the black player, assuming the white player is already assigned
            cursor.execute(
                """
                UPDATE Matches 
                SET black_player = %s 
                WHERE match_id = %s
            """,
                [player_username, match_id],
            )

        return redirect("/coach?message=Player assigned successfully!")

    except Exception as e:
        return redirect(f"/coach?error=Failed to assign player: {e}")


# Function to get all matches assigned to the coach (the coach's team is team2)
def get_coach_assigned_matches(username):
    matches = []
    try:
        with connection.cursor() as cursor:
            # Get matches assigned to the coach (where team2_id matches)
            cursor.execute(
                """
                SELECT m.match_id, m.date, m.time_slot,
                    h.hall_name, t.table_id,
                    t1.team_name AS team1_name, t2.team_name AS team2_name,
                    CONCAT(p1.name, ' ', p1.surname) AS white_player_name,
                    CONCAT(p2.name, ' ', p2.surname) AS black_player_name,
                    CONCAT(a.name, ' ', a.surname) AS arbiter_name,
                    m.team2_id AS coach_team_id
                FROM Matches m
                JOIN Halls h ON m.hall_id = h.hall_id
                JOIN Tables t ON m.table_id = t.table_id
                JOIN Teams t1 ON m.team1_id = t1.team_id
                JOIN Teams t2 ON m.team2_id = t2.team_id
                JOIN Arbiters a ON m.arbiter_username = a.username
                JOIN Players p1 ON m.white_player = p1.username
                LEFT JOIN Players p2 ON m.black_player = p2.username
                WHERE m.team2_id IN (
                    SELECT ct.team_id
                    FROM CoachTeams ct
                    WHERE ct.username = %s
                    AND m.date BETWEEN ct.contract_start AND ct.contract_finish
                )
                AND m.coach_username != %s
                ORDER BY m.date, m.time_slot""",
                [username, username],
            )
            rows = cursor.fetchall()

            for row in rows:
                formatted_match = list(row)
                formatted_match[1] = format_date_for_display(row[1])
                matches.append(formatted_match)

    except Exception as e:
        print(f"Error fetching coach assigned matches: {e}")
    return matches


# Function to get all available players for a given team, date, and time slot
def get_available_players_for_team(request):
    # Get team_id, date, and time_slot from the request
    team_id = request.GET.get("team_id")
    date = request.GET.get("date")
    db_date = format_date_for_db(date)
    time_slot = request.GET.get("time_slot")

    players = []
    try:
        with connection.cursor() as cursor:
            # Get available players for the selected date and time slot in the selected team
            cursor.execute(
                """
                SELECT p.username, CONCAT(p.name, ' ', p.surname, ' (', p.title, ', ', p.elo_rating, ')')
                FROM Players p
                JOIN PlayerTeams pt ON p.username = pt.username
                WHERE pt.team_id = %s
                AND p.username NOT IN (
                    SELECT m.white_player
                    FROM Matches m
                    WHERE m.date = %s AND m.time_slot = %s AND m.white_player IS NOT NULL
                    UNION
                    SELECT m.black_player
                    FROM Matches m
                    WHERE m.date = %s AND m.time_slot = %s AND m.black_player IS NOT NULL
                )
                ORDER BY p.name, p.surname
            """,
                [team_id, db_date, time_slot, db_date, time_slot],
            )
            players = cursor.fetchall()

    except Exception as e:
        print(f"Error fetching available players: {e}")

    return JsonResponse(list(players), safe=False)


# Function to get all the necessary context data for the coach view
def get_context_data(username):
    return {
        "username": username,
        "halls": get_all_halls(),
        "created_matches": get_coach_created_matches(username),
        "assigned_matches": get_coach_assigned_matches(username),
        "team": get_coach_team(username),
        "opponent_teams": get_opponent_teams(username),
    }
