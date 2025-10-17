from django import forms
from .models import Device, DeviceAccess


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'description', 'device_type', 'device_id']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': ' '
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': ' ',
                'rows': 3
            }),
            'device_type': forms.Select(attrs={
                'class': 'form-input'
            }),
            'device_id': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': ' ',
                'help_text': 'Unique identifier for this device (e.g., MAC address, serial number)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label_suffix = ''


class DeviceShareForm(forms.ModelForm):
    class Meta:
        model = DeviceAccess
        fields = ['user', 'permission_level']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-input'
            }),
            'permission_level': forms.Select(attrs={
                'class': 'form-input'
            }),
        }

    def __init__(self, group=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if group:
            # Limit users to group members only
            self.fields['user'].queryset = group.members.all()
        
        for field_name, field in self.fields.items():
            field.label_suffix = ''