from django.urls import path
from . import views

app_name = 'geografia'

urlpatterns = [
    # A URL que nosso JavaScript está procurando
    path('get-bairros/', views.get_bairros, name='get_bairros'),
]