from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser or self.user_permissions.filter(codename=perm).exists()

    def has_module_perms(self, app_label):
        return self.is_superuser or self.user_permissions.filter(content_type__app_label=app_label).exists()
    

class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    head = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    head = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dept')

    def __str__(self):
        return self.name



class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    ]

    STATUS_CHOICES = [

        ('Not Assigned', 'Not Assigned'),
        ('Acknowledged', 'Acknowledged'),
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Reopened', 'Reopened'),
        ('Closed', 'Closed'),
    ]
    TASK_TYPE_CHOICES = [

        ('Query', 'Query'),
        ('Techinical Issue', 'Techinical Issue'),
        ('Request', 'Request'),
        ('Other', 'Other')
    ]

    title = models.CharField(max_length=200)
    uuid = models.CharField(max_length=8, unique=True, editable=False, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES, default='Other')
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='L')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Not Assigned')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='dept')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    completed_at = models.DateTimeField(null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)  # Add this field
    def save(self, *args, **kwargs):
            if not self.uuid:
                self.uuid = str(uuid.uuid4())[:8]  # Generate and store the first 8 characters of the UUID
            super(Task, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"



class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.task.title}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"


