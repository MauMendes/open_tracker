from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Max, Avg, Min
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import models
from datetime import timedelta
import json
import csv
import io

from .models import Group, GroupMembership, Device, DeviceAccess, RegistrationRequest, DeviceData, DashboardWidget
from .forms import DeviceForm, DeviceShareForm


def is_superuser(user):
    return user.is_superuser


def is_group_admin(user, group_id=None):
    if user.is_superuser:
        return True
    if group_id:
        return GroupMembership.objects.filter(
            user=user, group_id=group_id, role='admin'
        ).exists()
    return GroupMembership.objects.filter(user=user, role='admin').exists()


@login_required
@user_passes_test(is_superuser)
def create_group(request):
    """Create a new group (superuser only)"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name:
            group = Group.objects.create(
                name=name,
                description=description,
                created_by=request.user
            )
            messages.success(request, f'Group "{group.name}" created successfully!')
            return redirect('iot:create_group')
    
    # Handle search and pagination
    search_query = request.GET.get('search', '')
    per_page = int(request.GET.get('per_page', 10))
    
    groups = Group.objects.all()
    
    if search_query:
        groups = groups.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(created_by__username__icontains=search_query)
        )
    
    groups = groups.order_by('name')
    
    # Pagination
    paginator = Paginator(groups, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'groups': page_obj,  # For backward compatibility
        'search_query': search_query,
        'per_page': per_page,
        'total_groups': Group.objects.count(),
    }
    return render(request, 'iot/create_group.html', context)


@login_required
@user_passes_test(is_superuser)
def update_group(request, group_id):
    """Update a group (superuser only)"""
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name:
            group.name = name
            group.description = description
            group.save()
            messages.success(request, f'Group "{group.name}" updated successfully!')
            return redirect('iot:create_group')
    
    context = {
        'group': group,
        'is_update': True,
    }
    return render(request, 'iot/update_group.html', context)


@login_required
@user_passes_test(is_superuser)
def delete_group(request, group_id):
    """Delete a group (superuser only)"""
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f'Group "{group_name}" deleted successfully!')
        return redirect('iot:create_group')
    
    context = {
        'group': group,
        'member_count': group.memberships.count(),
        'device_count': group.devices.count(),
    }
    return render(request, 'iot/delete_group.html', context)


@login_required
@user_passes_test(is_superuser)
def admin_dashboard(request):
    """Admin dashboard with data statistics and management options"""
    # Get data statistics
    total_devices = Device.objects.count()
    total_groups = Group.objects.count()
    total_users = User.objects.count()
    total_data_entries = DeviceData.objects.count()
    
    # Data by device type
    device_type_stats = Device.objects.values('device_type').annotate(
        device_count=Count('id'),
        data_count=Count('sensor_data')
    ).order_by('device_type')
    
    # Data by group
    group_stats = Group.objects.annotate(
        device_count=Count('devices'),
        data_count=Count('devices__sensor_data')
    ).order_by('name')
    
    # Recent data activity (last 24 hours)
    last_24h = timezone.now() - timedelta(hours=24)
    recent_data_count = DeviceData.objects.filter(timestamp__gte=last_24h).count()
    
    # Data size estimation (rough)
    avg_record_size = 100  # bytes per record estimate
    estimated_db_size = total_data_entries * avg_record_size
    
    context = {
        'total_devices': total_devices,
        'total_groups': total_groups,
        'total_users': total_users,
        'total_data_entries': total_data_entries,
        'device_type_stats': device_type_stats,
        'group_stats': group_stats,
        'recent_data_count': recent_data_count,
        'estimated_db_size': estimated_db_size,
        'devices': Device.objects.all().order_by('name'),
        'groups': Group.objects.all().order_by('name'),
    }
    
    return render(request, 'iot/admin_dashboard.html', context)


@login_required
@user_passes_test(is_superuser)
def registration_requests(request):
    """View for superusers to review registration requests"""
    requests_list = RegistrationRequest.objects.filter(status='pending')
    groups = Group.objects.all()
    
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        reg_request = get_object_or_404(RegistrationRequest, id=request_id)
        
        if action == 'approve':
            group_id = request.POST.get('group_id')
            role = request.POST.get('role', 'member')
            
            if group_id:
                group = get_object_or_404(Group, id=group_id)
                
                # Create group membership
                GroupMembership.objects.create(
                    group=group,
                    user=reg_request.user,
                    role=role,
                    approved_by=request.user
                )
                
                # Update registration request
                reg_request.status = 'approved'
                reg_request.reviewed_by = request.user
                reg_request.reviewed_at = timezone.now()
                reg_request.assigned_group = group
                reg_request.save()
                
                messages.success(request, f'User {reg_request.user.username} approved and added to {group.name}')
            
        elif action == 'reject':
            reg_request.status = 'rejected'
            reg_request.reviewed_by = request.user
            reg_request.reviewed_at = timezone.now()
            reg_request.admin_notes = request.POST.get('notes', '')
            reg_request.save()
            
            messages.success(request, f'Registration request from {reg_request.user.username} rejected')
        
        return redirect('iot:registration_requests')
    
    context = {
        'requests': requests_list,
        'groups': groups,
    }
    return render(request, 'iot/registration_requests.html', context)


@login_required
@user_passes_test(is_superuser)
def clean_device_data(request):
    """Clean data for specific scopes (all, device, or group)"""
    if request.method == 'POST':
        clean_type = request.POST.get('clean_type')
        target_id = request.POST.get('target_id')
        
        deleted_count = 0
        
        if clean_type == 'all':
            deleted_count = DeviceData.objects.all().delete()[0]
            messages.success(request, f'Deleted {deleted_count} data entries from all devices.')
            
        elif clean_type == 'device' and target_id:
            device = get_object_or_404(Device, id=target_id)
            deleted_count = DeviceData.objects.filter(device=device).delete()[0]
            messages.success(request, f'Deleted {deleted_count} data entries from device "{device.name}".')
            
        elif clean_type == 'group' and target_id:
            group = get_object_or_404(Group, id=target_id)
            deleted_count = DeviceData.objects.filter(device__group=group).delete()[0]
            messages.success(request, f'Deleted {deleted_count} data entries from group "{group.name}".')
            
        else:
            messages.error(request, 'Invalid cleaning parameters.')
    
    return redirect('myapp:index')


@login_required
def my_groups(request):
    """View user's groups - all groups for admin, user's groups for regular users"""
    
    if request.user.is_superuser:
        # Admin sees all groups
        search_query = request.GET.get('search', '')
        all_groups = Group.objects.all().order_by('name')
        
        if search_query:
            all_groups = all_groups.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(created_by__username__icontains=search_query)
            )
        
        # Handle pagination for admin
        per_page = request.GET.get('per_page', '10')
        try:
            per_page = int(per_page)
            if per_page not in [5, 10, 20]:
                per_page = 10
        except (ValueError, TypeError):
            per_page = 10
        
        paginator = Paginator(all_groups, per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Create fake memberships for admin view
        for group in page_obj:
            group.role = 'admin'
            group.membership_role = 'Admin'
        
        context = {
            'page_obj': page_obj,
            'selected_group': None,
            'per_page': per_page,
            'search_query': search_query,
            'total_groups': Group.objects.count(),  # Total count regardless of search
            'is_admin_view': True,
        }
        return render(request, 'iot/my_groups.html', context)
    
    # Regular user logic - show their memberships
    user_memberships = GroupMembership.objects.filter(user=request.user).select_related('group')
    
    # Handle pagination for regular users
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
        if per_page not in [5, 10, 20]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    
    paginator = Paginator(user_memberships, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get selected group from session (not needed anymore since devices show all groups)
    selected_group_id = request.session.get('selected_group_id')
    selected_group = None
    if selected_group_id:
        try:
            selected_group = Group.objects.get(id=selected_group_id)
            # Verify user is still member of this group
            if not user_memberships.filter(group=selected_group).exists():
                selected_group = None
        except Group.DoesNotExist:
            selected_group = None

    context = {
        'page_obj': page_obj,
        'selected_group': selected_group,
        'per_page': per_page,
        'total_groups': user_memberships.count(),
        'is_admin_view': False,
    }
    return render(request, 'iot/my_groups.html', context)


@login_required
def switch_group(request, group_id):
    """Switch to a different group"""
    group = get_object_or_404(Group, id=group_id)
    
    # Verify user is member of this group
    if not GroupMembership.objects.filter(user=request.user, group=group).exists():
        messages.error(request, 'You are not a member of this group.')
        return redirect('iot:my_groups')
    
    request.session['selected_group_id'] = group_id
    messages.success(request, f'Switched to group: {group.name}')
    return redirect('iot:group_devices')


@login_required
def group_devices(request):
    """View devices - all devices for admin, all user's group devices for regular users"""
    
    # If user is superuser, show all devices
    if request.user.is_superuser:
        # Handle search
        search_query = request.GET.get('search', '')
        devices = Device.objects.all().select_related('owner', 'group')
        
        if search_query:
            devices = devices.filter(
                Q(name__icontains=search_query) |
                Q(device_type__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(device_id__icontains=search_query) |
                Q(owner__username__icontains=search_query) |
                Q(group__name__icontains=search_query)
            )
        
        devices = devices.order_by('name')
        
        # Handle pagination for admin view
        per_page = request.GET.get('per_page', '10')
        try:
            per_page = int(per_page)
            if per_page not in [5, 10, 20]:
                per_page = 10
        except (ValueError, TypeError):
            per_page = 10
        
        paginator = Paginator(devices, per_page)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Add access info to devices for admin
        for device in page_obj:
            device.user_permission = 'admin'
            device.is_owner = device.owner == request.user
            device.can_control = True
            device.can_view = True

        context = {
            'page_obj': page_obj,
            'is_admin_view': True,
            'group': None,
            'membership': None,
            'search_query': search_query,
            'per_page': per_page,
            'total_devices': Device.objects.count(),
        }
        return render(request, 'iot/group_devices.html', context)
    
    # Regular user logic - show devices from ALL their groups
    user_groups = GroupMembership.objects.filter(user=request.user).values_list('group_id', flat=True)
    if not user_groups:
        return redirect('iot:my_groups')
    
    # Handle search for regular users - across all their groups
    search_query = request.GET.get('search', '')
    devices = Device.objects.filter(group_id__in=user_groups).select_related('owner', 'group')
    
    if search_query:
        devices = devices.filter(
            Q(name__icontains=search_query) |
            Q(device_type__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(device_id__icontains=search_query) |
            Q(owner__username__icontains=search_query) |
            Q(group__name__icontains=search_query)
        )
    
    devices = devices.order_by('group__name', 'name')
    
    # Get user's device access permissions across all groups
    user_device_access = DeviceAccess.objects.filter(
        user=request.user, device__group_id__in=user_groups
    ).select_related('device')
    
    access_map = {access.device_id: access.permission_level for access in user_device_access}
    
    # Handle pagination for regular users
    per_page = request.GET.get('per_page', '10')
    try:
        per_page = int(per_page)
        if per_page not in [5, 10, 20]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    
    paginator = Paginator(devices, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add access info to devices
    for device in page_obj:
        device.user_permission = access_map.get(device.id, None)
        device.is_owner = device.owner == request.user
        device.can_control = device.is_owner or device.user_permission == 'admin'
        device.can_view = device.is_owner or device.user_permission in ['admin', 'reader']

    # Get total counts for context
    total_devices = Device.objects.filter(group_id__in=user_groups).count()
    total_groups = len(user_groups)

    context = {
        'page_obj': page_obj,
        'is_admin_view': False,
        'search_query': search_query,
        'per_page': per_page,
        'total_devices': total_devices,
        'total_groups': total_groups,
        'group': None,  # No single group since showing all
        'membership': None,
    }
    return render(request, 'iot/group_devices.html', context)


@login_required
def create_device(request):
    """Create a new device"""
    # For superusers, allow them to choose any group
    if request.user.is_superuser:
        group_id = request.GET.get('group_id') or request.POST.get('group_id')
        
        if not group_id:
            # Redirect to group selection for admin
            available_groups = Group.objects.all()
            if available_groups.count() == 0:
                messages.error(request, 'No groups available. Please create a group first.')
                return redirect('iot:create_group')
            elif available_groups.count() == 1:
                # Auto-select the only available group
                group = available_groups.first()
            else:
                # Show group selection form
                context = {
                    'available_groups': available_groups,
                    'is_group_selection': True,
                }
                return render(request, 'iot/create_device.html', context)
        else:
            group = get_object_or_404(Group, id=group_id)
    else:
        # Regular user logic - requires selected group
        selected_group_id = request.session.get('selected_group_id')
        if not selected_group_id:
            return redirect('iot:my_groups')
        
        group = get_object_or_404(Group, id=selected_group_id)
        
        # Verify user is member of this group
        if not GroupMembership.objects.filter(user=request.user, group=group).exists():
            messages.error(request, 'You are not a member of this group.')
            return redirect('iot:my_groups')
    
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.group = group
            device.owner = request.user
            device.save()
            
            messages.success(request, f'Device "{device.name}" created successfully!')
            return redirect('iot:group_devices')
    else:
        form = DeviceForm()
    
    context = {
        'form': form,
        'group': group,
        'is_admin': request.user.is_superuser,
    }
    return render(request, 'iot/create_device.html', context)


@login_required
def device_detail(request, device_id):
    """View device details and manage sharing"""
    device = get_object_or_404(Device, id=device_id)
    
    # Check if user has access to this device
    membership = GroupMembership.objects.filter(user=request.user, group=device.group).first()
    if not membership and not request.user.is_superuser:
        messages.error(request, 'You do not have access to this device.')
        return redirect('iot:group_devices')
    
    # Get user's permission for this device
    device_access = DeviceAccess.objects.filter(user=request.user, device=device).first()
    is_owner = device.owner == request.user
    is_group_admin = membership and membership.role == 'admin'
    is_super_admin = request.user.is_superuser
    
    can_manage = is_owner or is_group_admin or is_super_admin
    can_control = is_owner or (device_access and device_access.permission_level == 'admin')
    can_view = is_owner or device_access or is_group_admin or is_super_admin
    
    if not can_view:
        messages.error(request, 'You do not have permission to view this device.')
        return redirect('iot:group_devices')
    
    # Get current device sharing
    device_shares = DeviceAccess.objects.filter(device=device).select_related('user')
    
    context = {
        'device': device,
        'device_shares': device_shares,
        'can_manage': can_manage,
        'can_control': can_control,
        'is_owner': is_owner,
        'is_group_admin': is_group_admin,
    }
    return render(request, 'iot/device_detail.html', context)


@login_required
def share_device(request, device_id):
    """Share device with other group members"""
    device = get_object_or_404(Device, id=device_id)
    
    # Check if user can manage this device
    membership = GroupMembership.objects.filter(user=request.user, group=device.group).first()
    if not membership and not request.user.is_superuser:
        messages.error(request, 'You do not have access to this device.')
        return redirect('iot:my_groups')
    
    is_owner = device.owner == request.user
    is_group_admin = membership and membership.role == 'admin'
    is_super_admin = request.user.is_superuser
    
    if not (is_owner or is_group_admin or is_super_admin):
        messages.error(request, 'You do not have permission to share this device.')
        return redirect('iot:device_detail', device_id=device.id)
    
    # Get group members who can be granted access
    group_members = User.objects.filter(
        group_memberships__group=device.group
    ).exclude(id=device.owner.id)
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        permission_level = request.POST.get('permission_level')
        
        if user_id and permission_level:
            user = get_object_or_404(User, id=user_id)
            
            # Verify user is in the same group
            if not GroupMembership.objects.filter(user=user, group=device.group).exists():
                messages.error(request, 'User is not a member of this group.')
                return redirect('iot:share_device', device_id=device.id)
            
            # Create or update device access
            device_access, created = DeviceAccess.objects.update_or_create(
                device=device,
                user=user,
                defaults={
                    'permission_level': permission_level,
                    'granted_by': request.user
                }
            )
            
            if created:
                messages.success(request, f'Granted {permission_level} access to {user.username}')
            else:
                messages.success(request, f'Updated {user.username} access to {permission_level}')
            
            return redirect('iot:device_detail', device_id=device.id)
    
    context = {
        'device': device,
        'group_members': group_members,
    }
    return render(request, 'iot/share_device.html', context)


@login_required
def revoke_device_access(request, device_id, user_id):
    """Revoke user's access to a device"""
    device = get_object_or_404(Device, id=device_id)
    user = get_object_or_404(User, id=user_id)
    
    # Check permissions
    membership = GroupMembership.objects.filter(user=request.user, group=device.group).first()
    if not membership and not request.user.is_superuser:
        messages.error(request, 'You do not have access to this device.')
        return redirect('iot:my_groups')
    
    is_owner = device.owner == request.user
    is_group_admin = membership.role == 'admin'
    is_superuser = request.user.is_superuser
    
    if not (is_owner or is_group_admin or is_superuser):
        messages.error(request, 'You do not have permission to manage this device.')
        return redirect('iot:device_detail', device_id=device.id)
    
    # Remove access
    device_access = DeviceAccess.objects.filter(device=device, user=user).first()
    if device_access:
        device_access.delete()
        messages.success(request, f'Revoked {user.username} access to {device.name}')
    
    return redirect('iot:device_detail', device_id=device.id)


@login_required
def edit_device(request, device_id):
    """Edit a device (owner, group admin, or superuser only)"""
    device = get_object_or_404(Device, id=device_id)
    
    # Check permissions
    membership = GroupMembership.objects.filter(user=request.user, group=device.group).first()
    if not membership and not request.user.is_superuser:
        messages.error(request, 'You do not have access to this device.')
        return redirect('iot:my_groups')
    
    is_owner = device.owner == request.user
    is_group_admin = membership and membership.role == 'admin'
    is_superuser = request.user.is_superuser
    
    if not (is_owner or is_group_admin or is_superuser):
        messages.error(request, 'You do not have permission to edit this device.')
        return redirect('iot:device_detail', device_id=device.id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        device_type = request.POST.get('device_type', '').strip()
        
        if not name:
            messages.error(request, 'Device name is required.')
        else:
            device.name = name
            device.description = description
            device.device_type = device_type
            device.save()
            
            messages.success(request, f'Device "{device.name}" updated successfully!')
            return redirect('iot:device_detail', device_id=device.id)
    
    return render(request, 'iot/edit_device.html', {
        'device': device,
        'can_manage': True
    })

@login_required
def delete_device(request, device_id):
    """Delete a device (owner, group admin, or superuser only)"""
    device = get_object_or_404(Device, id=device_id)
    
    # Check permissions
    membership = GroupMembership.objects.filter(user=request.user, group=device.group).first()
    if not membership and not request.user.is_superuser:
        messages.error(request, 'You do not have access to this device.')
        return redirect('iot:my_groups')
    
    is_owner = device.owner == request.user
    is_group_admin = membership and membership.role == 'admin'
    is_superuser = request.user.is_superuser
    
    if not (is_owner or is_group_admin or is_superuser):
        messages.error(request, 'You do not have permission to delete this device.')
        return redirect('iot:device_detail', device_id=device.id)
    
    if request.method == 'POST':
        device_name = device.name
        group_name = device.group.name
        device.delete()
        messages.success(request, f'Device "{device_name}" deleted successfully!')
        return redirect('iot:group_devices')
    
    context = {
        'device': device,
        'shared_users_count': device.access_permissions.count(),
    }
    return render(request, 'iot/delete_device.html', context)


@login_required
def dashboard(request):
    """Personal IoT Dashboard with device visualizations"""
    
    # Get user's dashboard widgets (only devices they've chosen to display)
    user_widgets = DashboardWidget.objects.filter(user=request.user).select_related('device', 'device__group', 'device__owner')
    
    # Get available devices for adding to dashboard
    if request.user.is_superuser:
        available_devices = Device.objects.all().select_related('group', 'owner')
    else:
        user_groups = GroupMembership.objects.filter(user=request.user).values_list('group_id', flat=True)
        available_devices = Device.objects.filter(group_id__in=user_groups).select_related('group', 'owner')
    
    # Exclude devices already on dashboard
    displayed_device_ids = user_widgets.values_list('device_id', flat=True)
    available_devices = available_devices.exclude(id__in=displayed_device_ids)
    
    # Get device data and organize by type
    dashboard_widgets = []
    
    for widget in user_widgets:
        device = widget.device
        # Get latest sensor data for each device
        latest_data = []
        for data_type in ['temperature', 'humidity', 'pressure', 'light', 'motion', 'location', 'speed', 'ignition']:
            latest_reading = DeviceData.objects.filter(
                device=device, 
                data_type=data_type
            ).order_by('-timestamp').first()
            
            if latest_reading:
                latest_data.append({
                    'data_type': data_type,
                    'latest_value': latest_reading.value,
                    'latest_timestamp': latest_reading.timestamp,
                    'unit': latest_reading.unit
                })
        
        # Get historical data for charts (last 24 hours)
        from datetime import timedelta
        from django.utils import timezone
        
        historical_data = DeviceData.objects.filter(
            device=device,
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).order_by('timestamp')
        
        widget_data = {
            'device': device,
            'latest_data': latest_data,
            'historical_data': historical_data,
            'widget_type': get_widget_type(device.device_type, device.name),
            'status': 'online' if device.is_active and device.last_seen and 
                     device.last_seen >= timezone.now() - timedelta(minutes=15) else 'offline'
        }
        dashboard_widgets.append(widget_data)
    
    # Dashboard statistics
    # Get all accessible devices for statistics
    if request.user.is_superuser:
        all_user_devices = Device.objects.all()
    else:
        user_groups = GroupMembership.objects.filter(user=request.user).values_list('group_id', flat=True)
        all_user_devices = Device.objects.filter(group_id__in=user_groups)
    
    total_devices = all_user_devices.count()
    
    # Calculate online/offline from all user devices, not just dashboard widgets
    online_devices = 0
    offline_devices = 0
    for device in all_user_devices:
        if device.is_active and device.last_seen and device.last_seen >= timezone.now() - timedelta(minutes=15):
            online_devices += 1
        else:
            offline_devices += 1
    
    device_types = all_user_devices.values('device_type').annotate(count=models.Count('id'))
    
    context = {
        'dashboard_widgets': dashboard_widgets,
        'available_devices': available_devices,
        'total_devices': total_devices,
        'online_devices': online_devices,
        'offline_devices': offline_devices,
        'device_types': device_types,
    }
    
    return render(request, 'iot/dashboard.html', context)


@login_required
def add_to_dashboard(request, device_id):
    """Add a device to user's personal dashboard"""
    device = get_object_or_404(Device, id=device_id)
    
    # Check permissions
    if not request.user.is_superuser:
        user_groups = GroupMembership.objects.filter(user=request.user).values_list('group_id', flat=True)
        if device.group_id not in user_groups:
            messages.error(request, 'You do not have access to this device.')
            return redirect('iot:dashboard')
    
    # Add to dashboard if not already there
    widget, created = DashboardWidget.objects.get_or_create(
        user=request.user,
        device=device,
        defaults={'position': DashboardWidget.objects.filter(user=request.user).count()}
    )
    
    if created:
        messages.success(request, f'Added "{device.name}" to your dashboard.')
    else:
        messages.info(request, f'"{device.name}" is already on your dashboard.')
    
    return redirect('iot:dashboard')


@login_required
def remove_from_dashboard(request, device_id):
    """Remove a device from user's personal dashboard"""
    device = get_object_or_404(Device, id=device_id)
    
    try:
        widget = DashboardWidget.objects.get(user=request.user, device=device)
        widget.delete()
        messages.success(request, f'Removed "{device.name}" from your dashboard.')
    except DashboardWidget.DoesNotExist:
        messages.error(request, f'"{device.name}" is not on your dashboard.')
    
    return redirect('iot:dashboard')


def get_widget_type(device_type, device_name=''):
    """Determine widget visualization type based on device type and name"""
    # Special handling for air quality monitors
    if 'air quality' in device_name.lower():
        return 'gauge'
    
    widget_mapping = {
        'sensor': 'gauge',
        'thermostat': 'temperature_gauge',
        'light': 'switch_control',
        'camera': 'camera_feed',
        'lock': 'lock_status',
        'speaker': 'audio_control',
        'hub': 'status_indicator',
        'actuator': 'control_panel',
        'vehicle': 'vehicle_status',
        'other': 'generic_status'
    }
    return widget_mapping.get(device_type, 'generic_status')


@login_required
def dashboard_api_data(request, device_id):
    """API endpoint for real-time dashboard data"""
    device = get_object_or_404(Device, id=device_id)
    
    # Check permissions
    if not request.user.is_superuser:
        user_groups = GroupMembership.objects.filter(user=request.user).values_list('group_id', flat=True)
        if device.group_id not in user_groups:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get latest sensor data (SQLite-compatible approach)
    data_types = DeviceData.objects.filter(device=device).values_list('data_type', flat=True).distinct()
    latest_data = []
    for data_type in data_types:
        latest_reading = DeviceData.objects.filter(
            device=device, 
            data_type=data_type
        ).order_by('-timestamp').first()
        if latest_reading:
            latest_data.append({
                'data_type': latest_reading.data_type,
                'value': latest_reading.value,
                'unit': latest_reading.unit,
                'timestamp': latest_reading.timestamp
            })
    
    # Get recent historical data for mini charts
    from datetime import timedelta
    from django.utils import timezone
    
    historical_data = list(DeviceData.objects.filter(
        device=device,
        timestamp__gte=timezone.now() - timedelta(hours=6)
    ).values('data_type', 'value', 'timestamp').order_by('timestamp'))
    
    return JsonResponse({
        'device_id': device.id,
        'device_name': device.name,
        'device_type': device.device_type,
        'latest_data': latest_data,
        'historical_data': historical_data,
        'status': 'online' if device.is_active else 'offline',
        'last_seen': device.last_seen.isoformat() if device.last_seen else None
    })


def export_historical_data_csv(table_data, table_columns, start_date, end_date):
    """Export historical data to CSV format (Excel compatible)"""
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    
    # Generate filename with date range
    from django.utils import timezone as django_timezone
    start_str = django_timezone.localtime(start_date).strftime('%d-%m-%Y') if start_date else 'all'
    end_str = django_timezone.localtime(end_date).strftime('%d-%m-%Y') if end_date else 'all'
    filename = f'historical_data_{start_str}_to_{end_str}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    # Write header row
    headers = ['Timestamp', 'Device Name', 'Device ID', 'Device Type']
    for column in table_columns:
        headers.append(column.replace('_', ' ').title())
    writer.writerow(headers)
    
    # Write data rows
    for row in table_data:
        csv_row = [
            django_timezone.localtime(row['timestamp']).strftime('%d/%m/%Y %H:%M:%S'),
            row['device'].name,
            row['device'].device_id,
            row['device'].get_device_type_display(),
        ]
        
        # Add data columns
        for column in table_columns:
            value = row['data'].get(column, '-')
            csv_row.append(value)
        
        writer.writerow(csv_row)
    
    return response


@login_required
def historical_data(request):
    """View for analyzing historical sensor data with date/time filtering"""
    
    # Get all devices for the filter dropdown
    devices = Device.objects.all().order_by('name')
    
    # Initialize context
    context = {
        'devices': devices,
        'data_entries': [],
        'statistics': {},
        'selected_device': None,
        'start_date': None,
        'end_date': None,
        'data_type_filter': None,
    }
    
    if request.method == 'POST':
        device_id = request.POST.get('device_id')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        data_type_filter = request.POST.get('data_type_filter')
        export_format = request.POST.get('export')
        
        try:
            # Parse dates
            start_date = None
            end_date = None
            
            if start_date_str:
                start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M'))
                context['start_date'] = start_date_str
                
            if end_date_str:
                end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M'))
                context['end_date'] = end_date_str
            
            # Build query
            query = DeviceData.objects.all()
            
            if device_id:
                device = get_object_or_404(Device, id=device_id)
                query = query.filter(device=device)
                context['selected_device'] = device
                
            if start_date:
                query = query.filter(timestamp__gte=start_date)
                
            if end_date:
                query = query.filter(timestamp__lte=end_date)
                
            if data_type_filter:
                query = query.filter(data_type=data_type_filter)
                context['data_type_filter'] = data_type_filter
            
            # Get the data entries
            data_entries = query.select_related('device').order_by('-timestamp')[:1000]  # Limit to 1000 entries
            
            # Group entries by device and timestamp for table format
            grouped_entries = {}
            for entry in data_entries:
                # Convert UTC timestamp to local time for display and grouping
                from django.utils import timezone as django_timezone
                local_timestamp = django_timezone.localtime(entry.timestamp)
                timestamp_key = local_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                device_key = f"{entry.device.name}_{timestamp_key}"
                
                if device_key not in grouped_entries:
                    grouped_entries[device_key] = {
                        'device': entry.device,
                        'timestamp': local_timestamp,  # Use local timestamp for display
                        'data': {}
                    }
                
                # Store data by type for easy column access with custom formatting
                if entry.data_type == 'ignition':
                    # Convert ignition values to ON/OFF
                    if str(entry.value).lower() in ['1', '1.0', 'true', 'on']:
                        formatted_value = 'ON'
                    else:
                        formatted_value = 'OFF'
                elif entry.data_type == 'speed':
                    # Just show the speed value since unit is in column header
                    formatted_value = str(entry.value)
                elif entry.data_type == 'location':
                    # For location, use unit field if value is 0 (our client sends location name in unit field)
                    value_str = str(entry.value).strip()
                    if value_str in ['0.0', '0', '0.00'] and entry.unit:
                        formatted_value = entry.unit
                    elif value_str not in ['null', 'None', '', 'nan', 'NaN'] and value_str not in ['0.0', '0', '0.00']:
                        formatted_value = value_str
                    else:
                        formatted_value = '-'
                else:
                    # Default formatting for other data types
                    formatted_value = f"{entry.value}"
                    if entry.unit:
                        formatted_value += f" {entry.unit}"
                
                grouped_entries[device_key]['data'][entry.data_type] = formatted_value
            
            # Convert to list and sort by timestamp (descending)
            table_data = list(grouped_entries.values())
            table_data.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Determine columns based on device types in the filtered data
            device_types_in_data = set()
            for row in table_data:
                device_types_in_data.add(row['device'].device_type)
            
            # Define column mappings for different device types
            column_mappings = {
                'vehicle': ['ignition', 'speed', 'location'],
                'thermostat': ['temperature', 'humidity'],
                'sensor': ['temperature', 'humidity', 'pressure'],
            }
            
            # Get all possible data types from the current selection
            all_data_types = set()
            for row in table_data:
                all_data_types.update(row['data'].keys())
            
            # Create dynamic columns based on what's actually in the data
            table_columns = []
            for device_type in device_types_in_data:
                if device_type in column_mappings:
                    for col in column_mappings[device_type]:
                        if col in all_data_types and col not in table_columns:
                            table_columns.append(col)
            
            # Add any remaining data types not in predefined mappings
            for data_type in sorted(all_data_types):
                if data_type not in table_columns:
                    table_columns.append(data_type)
            
            context['data_entries'] = data_entries  # Keep original for count
            context['table_data'] = table_data
            context['table_columns'] = table_columns
            
            # Calculate statistics if we have data
            if data_entries:
                total_entries = query.count()
                
                # Get unique data types for this selection
                data_types = query.values_list('data_type', flat=True).distinct()
                
                # Calculate statistics by data type
                stats_by_type = {}
                for dtype in data_types:
                    type_data = query.filter(data_type=dtype)
                    stats_by_type[dtype] = {
                        'count': type_data.count(),
                        'avg': type_data.aggregate(Avg('value'))['value__avg'],
                        'min': type_data.aggregate(Min('value'))['value__min'],
                        'max': type_data.aggregate(Max('value'))['value__max'],
                    }
                
                # Convert date range to local time for display
                from django.utils import timezone as django_timezone
                start_local = django_timezone.localtime(start_date) if start_date else None
                end_local = django_timezone.localtime(end_date) if end_date else None
                
                context['statistics'] = {
                    'total_entries': total_entries,
                    'date_range': f"{start_local.strftime('%d/%m/%Y %H:%M') if start_local else 'Beginning'} to {end_local.strftime('%d/%m/%Y %H:%M') if end_local else 'Now'}",
                    'by_type': stats_by_type,
                    'data_types': list(data_types),
                }
                
            # Handle Excel export
            if export_format == 'excel':
                return export_historical_data_csv(table_data, table_columns, start_date, end_date)
                
            messages.success(request, f'Found {len(data_entries)} entries matching your criteria.')
            
        except ValueError as e:
            messages.error(request, f'Invalid date format: {e}')
        except Exception as e:
            messages.error(request, f'Error processing request: {e}')
    
    return render(request, 'iot/historical_data.html', context)