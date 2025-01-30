# timeline_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Milestone
from .forms import ProjectForm, MilestoneForm

@login_required
def dashboard(request):
    projects = Project.objects.filter(user=request.user)
    return render(request, 'timeline_app/dashboard.html', {'projects': projects})

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('dashboard')
    else:
        form = ProjectForm()
    return render(request, 'timeline_app/project_form.html', {'form': form})

@login_required
def milestone_create(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()
            messages.success(request, 'Milestone added successfully!')
            return redirect('project_detail', project_id=project.id)
    else:
        form = MilestoneForm()
    return render(request, 'timeline_app/milestone_form.html', {'form': form, 'project': project})