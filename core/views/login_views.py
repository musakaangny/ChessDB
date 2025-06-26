from django.shortcuts import render, redirect
from django.db import connection

from core.utils import hash_password


# View to handle "/login" page
def login(request):
    if request.method == "POST":
        # Get the form data from the request
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = request.POST.get("user_type")

        # Hash the password before checking
        hashed_password = hash_password(password)

        # Validate user type
        if user_type == "dbmanager":
            table_name = "DBManagers"
        elif user_type == "player":
            table_name = "Players"
        elif user_type == "coach":
            table_name = "Coaches"
        elif user_type == "arbiter":
            table_name = "Arbiters"
        else:
            return redirect(f"/?error=Invalid user type")

        try:
            with connection.cursor() as cursor:
                # Check if the user exists with the given username and password in the specified table
                sql = (
                    f"SELECT * FROM {table_name} WHERE username = %s AND password = %s"
                )
                cursor.execute(sql, [username, hashed_password])
                user = cursor.fetchone()

            if not user:
                return redirect(f"/?error=Invalid username or password")

            # Create a response object to set cookies
            response = redirect(f"/{user_type}?message=Login successful")

            # Set cookies for session information
            response.set_cookie("username", username)
            response.set_cookie("user_type", user_type)

            return response

        except Exception as e:
            return redirect(f"/?error=Database error: {str(e)}")

    # Get the error and message from the URL parameters of the request
    error = request.GET.get("error")
    message = request.GET.get("message")
    context = {"error": error, "message": message}

    return render(request, "core/login.html", context)


# View to handle logout
def logout(request):
    # Create response for redirect
    response = redirect("/?message=Logout successful")

    # Clear cookies
    response.delete_cookie("username")
    response.delete_cookie("user_type")

    return response
