from django import forms
from .models import Task, Attachment, Notification, Comment
from django.contrib.auth.forms import UserCreationForm
from .models import User



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')



class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'status', 'project', 'department', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = Attachment
        fields = ['file']

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['user', 'message']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']