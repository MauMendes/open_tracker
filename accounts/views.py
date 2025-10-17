from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q
from django import forms
from django.utils import timezone
from .forms import CustomUserCreationForm
from iot.models import RegistrationRequest, Group, GroupMembership
import datetime

def login_view(request):
    if request.user.is_authenticated:
        return redirect('myapp:index')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'myapp:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('myapp:index')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! You can now sign in.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

@login_required
def profile_view(request):
    user = request.user
    
    # Get user's group memberships
    from iot.models import GroupMembership
    user_memberships = GroupMembership.objects.filter(
        user=user
    ).select_related('group').order_by('group__name')
    
    context = {
        'user': user,
        'last_login': user.last_login,
        'date_joined': user.date_joined,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'user_memberships': user_memberships,
    }
    return render(request, 'accounts/profile.html', context)

# Helper function to check if user is superuser
def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def user_management_view(request):
    # Handle registration request actions
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        if request_id and action:
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
            
            return redirect('accounts:user_management')
    
    search_query = request.GET.get('search', '')
    per_page = request.GET.get('per_page', '10')
    
    # Validate per_page parameter
    try:
        per_page = int(per_page)
        if per_page not in [5, 10, 20]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    
    users = User.objects.all().order_by('-date_joined')

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    paginator = Paginator(users, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)    # Get registration requests
    registration_requests = RegistrationRequest.objects.filter(status='pending')
    groups = Group.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'per_page': per_page,
        'total_users': User.objects.count(),
        'registration_requests': registration_requests,
        'groups': groups,
    }
    return render(request, 'accounts/user_management.html', context)

class AdminUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    is_staff = forms.BooleanField(required=False, help_text='Allow user to access admin site')
    is_superuser = forms.BooleanField(required=False, help_text='Give user all permissions')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_superuser')

@user_passes_test(is_superuser)
def create_user_view(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" created successfully.')
            return redirect('accounts:user_management')
    else:
        form = AdminUserCreationForm()
    
    return render(request, 'accounts/create_user.html', {'form': form})

@user_passes_test(is_superuser)
def delete_user_view(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    
    # Prevent deletion of current user
    if user_to_delete == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('accounts:user_management')
    
    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f'User "{username}" deleted successfully.')
        return redirect('accounts:user_management')
    
    return render(request, 'accounts/confirm_delete.html', {'user_to_delete': user_to_delete})

class AdminUserEditForm(forms.ModelForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    is_staff = forms.BooleanField(required=False, help_text='Allow user to access admin site')
    is_superuser = forms.BooleanField(required=False, help_text='Give user all permissions')
    is_active = forms.BooleanField(required=False, help_text='User account is active')
    groups = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text='Select IoT groups this user should be a member of'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from iot.models import Group
        self.fields['groups'].queryset = Group.objects.all()
        
        # If editing existing user, set current groups
        if self.instance.pk:
            from iot.models import GroupMembership
            current_groups = Group.objects.filter(
                memberships__user=self.instance
            )
            self.fields['groups'].initial = current_groups

@user_passes_test(is_superuser)
def edit_user_view(request, user_id):
    user_to_edit = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            user = form.save()
            
            # Handle group memberships
            from iot.models import Group, GroupMembership
            selected_groups = form.cleaned_data['groups']
            
            # Remove user from groups not selected
            GroupMembership.objects.filter(user=user).exclude(
                group__in=selected_groups
            ).delete()
            
            # Add user to selected groups (if not already a member)
            for group in selected_groups:
                GroupMembership.objects.get_or_create(
                    user=user,
                    group=group,
                    defaults={
                        'role': 'member',
                        'approved_by': request.user
                    }
                )
            
            messages.success(request, f'User "{user.username}" updated successfully.')
            return redirect('accounts:user_management')
    else:
        form = AdminUserEditForm(instance=user_to_edit)
    
    context = {
        'form': form,
        'user_to_edit': user_to_edit,
    }
    return render(request, 'accounts/edit_user.html', context)
