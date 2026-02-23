from django.urls import path
from . import views

app_name = 'school'

urlpatterns = [
    path('', views.home, name='home'),
    path('team/', views.team_list, name='team_list'),
    path('<slug:slug>/', views.page_detail, name='page_detail'),
]
