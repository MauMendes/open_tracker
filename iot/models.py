from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class GroupMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Group Admin'),
        ('member', 'Member'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approved_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['group', 'user']
        ordering = ['group__name', 'user__username']

    def __str__(self):
        return f"{self.user.username} in {self.group.name} ({self.role})"


class Device(models.Model):
    DEVICE_TYPE_CHOICES = [
        ('sensor', 'Sensor'),
        ('actuator', 'Actuator'),
        ('camera', 'Camera'),
        ('thermostat', 'Temperature Sensor'),
        ('light', 'Smart Light'),
        ('lock', 'Smart Lock'),
        ('speaker', 'Smart Speaker'),
        ('hub', 'IoT Hub'),
        ('vehicle', 'Vehicle'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES)
    device_id = models.CharField(max_length=100, help_text="Unique device identifier")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='devices')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_devices')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['device_id', 'group']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.group.name})"

    def clean(self):
        # Skip owner validation during form processing
        # Owner validation is handled in the view
        pass


class DeviceAccess(models.Model):
    PERMISSION_CHOICES = [
        ('admin', 'Admin'),
        ('reader', 'Reader'),
    ]
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='access_permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_access')
    permission_level = models.CharField(max_length=10, choices=PERMISSION_CHOICES)
    granted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='granted_permissions')
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['device', 'user']
        ordering = ['device__name', 'user__username']

    def __str__(self):
        return f"{self.user.username} -> {self.device.name} ({self.permission_level})"

    def clean(self):
        # Ensure user is in the same group as the device
        if self.user and self.device:
            if not GroupMembership.objects.filter(user=self.user, group=self.device.group).exists():
                raise ValidationError("User must be a member of the device's group.")


class RegistrationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='registration_request')
    requested_group_info = models.TextField(help_text="Information about which group the user wants to join")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    assigned_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    admin_notes = models.TextField(blank=True, help_text="Internal notes for admins")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request by {self.user.username} - {self.status}"


class DeviceData(models.Model):
    """Store sensor data and device telemetry"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sensor_data')
    timestamp = models.DateTimeField(auto_now_add=True)
    data_type = models.CharField(max_length=50)  # temperature, humidity, motion, etc.
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)  # °C, %, lux, etc.
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'data_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.device.name} - {self.data_type}: {self.value} {self.unit}"


class DashboardWidget(models.Model):
    """Track which devices a user wants to display on their dashboard"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_widgets')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='dashboard_displays')
    position = models.IntegerField(default=0, help_text="Widget position on dashboard")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'device']
        ordering = ['position', 'created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.device.name}"
