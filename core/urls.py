from django.urls import path
from core.views import *

urlpatterns = [
    path('', TaskListView.as_view(), name='task-list'),
    path('admin_view/', admin_view, name='adminview'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/create/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/update/', TaskUpdateView.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task-delete'),
    path('tasks/<int:pk>/assign/', task_assign_view, name='task-assign'),
    path('tasks/<int:task_pk>/attachments/add/', add_attachment_view, name='add-attachment'),
    path('tasks/<int:task_pk>/notifications/send/', send_notification_view, name='send-notification'),
    path('tasks/<int:task_pk>/comments/add/', add_comment_view, name='add-comment'),
    path('notification/<int:notification_id>/mark-as-read/', mark_as_read, name='mark-as-read'),
    path('notifications/', user_notifications, name='user-notifications'),
    # path('task/<int:task_id>/create-notification/', create_notification, name='create-notification'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
]
