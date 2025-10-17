from django.urls import path
from . import views

app_name = 'iot'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/add/<int:device_id>/', views.add_to_dashboard, name='add_to_dashboard'),
    path('dashboard/remove/<int:device_id>/', views.remove_from_dashboard, name='remove_from_dashboard'),
    path('api/dashboard/<int:device_id>/', views.dashboard_api_data, name='dashboard_api_data'),
    
    # Group management
    path('', views.my_groups, name='my_groups'),
    path('switch/<int:group_id>/', views.switch_group, name='switch_group'),
    
    # Device management
    path('devices/', views.group_devices, name='group_devices'),
    path('devices/create/', views.create_device, name='create_device'),
    path('devices/<int:device_id>/', views.device_detail, name='device_detail'),
    path('devices/<int:device_id>/share/', views.share_device, name='share_device'),
    path('devices/<int:device_id>/revoke/<int:user_id>/', views.revoke_device_access, name='revoke_device_access'),
    path('devices/<int:device_id>/edit/', views.edit_device, name='edit_device'),
    
    # Admin views
    path('admin/requests/', views.registration_requests, name='registration_requests'),
    path('admin/data/clean/', views.clean_device_data, name='clean_device_data'),
    path('historical/', views.historical_data, name='historical_data'),
    path('admin/groups/create/', views.create_group, name='create_group'),
    path('admin/groups/<int:group_id>/update/', views.update_group, name='update_group'),
    path('admin/groups/<int:group_id>/delete/', views.delete_group, name='delete_group'),
    path('devices/<int:device_id>/delete/', views.delete_device, name='delete_device'),
]