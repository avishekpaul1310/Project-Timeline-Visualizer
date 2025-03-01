from django.contrib import admin
from .models import Project, Milestone, Notification

admin.site.register(Project)
admin.site.register(Milestone)
admin.site.register(Notification)