from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('manage-users/', views.user_management_view, name='user_management'),
    path('create-user/', views.create_user_view, name='create_user'),
    path('delete-user/<int:user_id>/', views.delete_user_view, name='delete_user'),
    path('edit-user/<int:user_id>/', views.edit_user_view, name='edit_user'),
]