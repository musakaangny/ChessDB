from django.urls import path
from core.views import player_views
from core.views import coach_views
from core.views import arbiter_views
from core.views import dbmanager_views
from core.views import login_views

urlpatterns = [
    path("", login_views.login, name="login"),
    path("logout", login_views.logout, name="logout"),
    path("arbiter", arbiter_views.arbiter, name="arbiter"),
    path("coach", coach_views.coach, name="coach"),
    path("dbmanager", dbmanager_views.dbmanager, name="dbmanager"),
    path("player", player_views.player, name="player"),
]
