from django.urls import path

from . import views

app_name = "user_profiles"

urlpatterns = [
    path("settings/", views.user_settings, name="user_settings"),
    path("productivity-data/", views.productivity_data, name="productivity_data"),
]
