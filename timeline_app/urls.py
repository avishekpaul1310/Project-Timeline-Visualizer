from django.urls import path
from . import views

app_name = 'timeline_app'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('project/create/', views.project_create, name='project_create'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/edit/', views.project_update, name='project_update'),
    path('project/<int:project_id>/delete/', views.project_delete, name='project_delete'),
    path('project/<int:project_id>/milestone/create/', views.milestone_create, name='milestone_create'),
    path('project/<int:project_id>/share/', views.share_project, name='share_project'),
    path('project/<int:project_id>/remove-collaborator/<int:user_id>/', views.remove_collaborator, name='remove_collaborator'),
    path('projects/archived/', views.archived_projects, name='archived_projects'),
    path('project/<int:project_id>/archive/', views.archive_project, name='archive_project'),
    path('project/<int:project_id>/unarchive/', views.unarchive_project, name='unarchive_project'),
    path('project/<int:project_id>/export/<str:format_type>/', views.export_project, name='export_project'),
    path('analytics/', views.analytics, name='analytics'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
]