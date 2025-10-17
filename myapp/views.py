from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from iot.models import GroupMembership, Device, DeviceData, Group

# Create your views here.

def index(request):
    context = {}
    
    if request.user.is_authenticated:
        if request.user.is_superuser:
            # Admin statistics
            total_devices = Device.objects.count()
            total_groups = Group.objects.count()
            total_users = User.objects.count()
            total_data_entries = DeviceData.objects.count()
            
            # Recent data activity (last 24 hours)
            last_24h = timezone.now() - timedelta(hours=24)
            recent_data_count = DeviceData.objects.filter(timestamp__gte=last_24h).count()
            
            # Data size estimation
            avg_record_size = 100  # bytes per record estimate
            estimated_db_size = total_data_entries * avg_record_size
            
            # Data by device type
            device_type_stats = Device.objects.values('device_type').annotate(
                device_count=Count('id'),
                data_count=Count('sensor_data')
            ).order_by('device_type')
            
            context.update({
                'admin_stats': {
                    'total_devices': total_devices,
                    'total_groups': total_groups, 
                    'total_users': total_users,
                    'total_data_entries': total_data_entries,
                    'recent_data_count': recent_data_count,
                    'estimated_db_size': estimated_db_size,
                    'device_type_stats': device_type_stats,
                },
                'devices': Device.objects.all().order_by('name'),
                'groups': Group.objects.all().order_by('name'),
            })
        else:
            # Get user's group memberships with counts
            user_memberships = GroupMembership.objects.filter(user=request.user).select_related('group')
            
            group_info = []
            total_devices = 0
            
            for membership in user_memberships:
                device_count = Device.objects.filter(group=membership.group).count()
                member_count = GroupMembership.objects.filter(group=membership.group).count()
                
                group_info.append({
                    'group': membership.group,
                    'role': membership.get_role_display(),
                    'device_count': device_count,
                    'member_count': member_count,
                })
                total_devices += device_count
            
            context.update({
                'user_groups': group_info,
                'total_groups': len(group_info),
                'total_devices': total_devices,
            })
    
    return render(request, 'myapp/home.html', context)

def admin_stats_api(request):
    """API endpoint for real-time admin statistics"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Calculate statistics
    total_devices = Device.objects.count()
    total_groups = Group.objects.count()
    total_users = User.objects.count()
    total_data_entries = DeviceData.objects.count()
    
    # Calculate data size
    data_size_kb = total_data_entries * 0.1  # Rough estimate
    
    # Calculate recent entries (last 24 hours)
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    recent_entries = DeviceData.objects.filter(timestamp__gte=twenty_four_hours_ago).count()
    
    return JsonResponse({
        'total_devices': total_devices,
        'total_groups': total_groups,
        'total_users': total_users,
        'total_data_entries': total_data_entries,
        'data_size_kb': data_size_kb,
        'recent_entries': recent_entries,
    })
