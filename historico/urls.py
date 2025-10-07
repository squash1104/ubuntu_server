from django.urls import path

from . import views

app_name = "historico"

urlpatterns = [
    path("", views.historico_list, name="historico_list"),
    path("<int:pk>/", views.historico_detail, name="historico_detail"),
]
