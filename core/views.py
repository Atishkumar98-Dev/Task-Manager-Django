from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from core.models import Task, User
from core.forms import TaskForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.views import LogoutView
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import user_passes_test
from .models import Task, Attachment, Notification, Comment
from .forms import TaskForm, AttachmentForm, NotificationForm, CommentForm
from django.db.models import Count


def is_super_admin(user):
    return user.is_superuser


@user_passes_test(is_super_admin)
def admin_view(request):
    # Get all tasks
    all_tasks = Task.objects.all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        all_tasks = all_tasks.filter(title__icontains=search_query)

    # Filtering based on status
    status_filter = request.GET.get('status', '')
    if status_filter:
        all_tasks = all_tasks.filter(status=status_filter)

    # Count tasks based on status
    count_task = all_tasks.count()
    count_successful = all_tasks.filter(status='Resolved').count()
    count_pending = all_tasks.filter(status='Pending').count()
    count_reopen = all_tasks.filter(status='Reopened').count()
    count_acknowledged = all_tasks.filter(status='Acknowledged').count()
    count_closed = all_tasks.filter(status='Closed').count()
    count_assigned = all_tasks.exclude(assigned_to=None).count()
    count_not_assigned = all_tasks.filter(assigned_to=None).count()

    # User-wise task count
    user_task_counts = User.objects.annotate(task_count=Count('tasks'))

    context = {
        'all_tasks': all_tasks,
        'count_task': count_task,
        'count_reopen': count_reopen,
        'count_acknowledged': count_acknowledged,
        'count_closed': count_closed,
        'count_successful': count_successful,
        'count_pending': count_pending,
        'count_assigned': count_assigned,
        'count_not_assigned': count_not_assigned,
        'user_task_counts': user_task_counts,
        'search_query': search_query,
        'status_filter': status_filter
    }
    return render(request, 'adminview.html', context)


@user_passes_test(is_super_admin)
def task_assign_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task-list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'task_assign.html', {'form': form, 'task': task})


def add_attachment_view(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.task = task
            attachment.save()
            return redirect('task-detail', pk=task_pk)
    else:
        form = AttachmentForm()
    return render(request, 'add_attachment.html', {'form': form, 'task': task})

def send_notification_view(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.task = task
            notification.save()
            return redirect('task-detail', pk=task_pk)
    else:
        form = NotificationForm()
    return render(request, 'send_notification.html', {'form': form, 'task': task})

def add_comment_view(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.author = request.user
            comment.save()
            return redirect('task-detail', pk=task_pk)
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form, 'task': task})



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect(reverse('task-list'))  # Redirect to a page after login
        else:
            return render(request, 'login.html', {'error': 'Invalid email or password'})
    return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Automatically log in the user after registration
            return redirect(reverse('task-list'))  # Redirect to a page after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect(reverse('login'))


# Task List View
class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        project_id = self.request.GET.get('project')
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset.filter(assigned_to=user)
    
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    if notification.user == request.user:  # Ensure the user owns the notification
        notification.read = True
        notification.save()
    return redirect('user-notifications')

def user_notifications(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    return render(request, 'user_notifications.html', {'notifications': notifications})
# Task Detail View
class TaskDetailView(DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        context['attachments'] = task.attachments.all()
        context['comments'] = task.comments.all()
        context['notifications'] = task.notifications.all()
        if self.request.user.is_authenticated:
            context['unread_notifications_count'] = self.request.user.notifications.filter(read=False).count()
            print(Notification.objects.filter(user=self.request.user, read=False).count())
        return context

# Task Create View
class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user  # Automatically set the user who creates the task
        return super().form_valid(form)

# Task Update View
class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task-list')

# Task Delete View
class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('task-list')
