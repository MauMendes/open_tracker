from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from iot.models import RegistrationRequest


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=False, help_text='Optional. We will use this for account recovery.')
    group_request_info = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Please describe which group you would like to join and why...'}),
        label='Group Request Information',
        help_text='Tell us which group you want to join (e.g., "Johnson Family Home", "Office Building A") and why you need access.',
        max_length=500
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'group_request_info')

    def save(self, commit=True):
        user = super().save(commit)
        if commit:
            # Create a registration request
            RegistrationRequest.objects.create(
                user=user,
                requested_group_info=self.cleaned_data['group_request_info']
            )
        return user