from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('project/create/', views.project_create, name='project_create'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/milestone/create/', views.milestone_create, name='milestone_create'),
    path('project/<int:project_id>/edit/', views.project_update, name='project_update'),
    path('project/<int:project_id>/delete/', views.project_delete, name='project_delete'),
]