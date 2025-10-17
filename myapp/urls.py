from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/admin-stats/', views.admin_stats_api, name='admin_stats_api'),
]