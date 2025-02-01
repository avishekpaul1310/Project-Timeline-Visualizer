# timeline_app/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Milestone
from .forms import ProjectForm, MilestoneForm
import json
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def dashboard(request):
    projects = Project.objects.filter(user=request.user)
    # Serialize projects for the chart
    projects_data = json.loads(serialize('json', projects))
    projects_list = [{'name': p['fields']['name'],
                     'start_date': p['fields']['start_date'],
                     'end_date': p['fields']['end_date']} 
                    for p in projects_data]
    
    return render(request, 'timeline_app/dashboard.html', {
        'projects': projects,
        'projects_json': json.dumps(projects_list, cls=DjangoJSONEncoder)
    })
@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, 'Project created successfully!')
            return redirect('timeline_app:dashboard')
    else:
        form = ProjectForm()
    return render(request, 'timeline_app/project_form.html', {'form': form})

@login_required
def milestone_create(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        form = MilestoneForm(request.POST, project=project)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()
            messages.success(request, 'Milestone added successfully!')
            return redirect('timeline_app:project_detail', project_id=project.id)
    else:
        form = MilestoneForm(project=project)
    return render(request, 'timeline_app/milestone_form.html', {
        'form': form,
        'project': project
    })

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    milestones = project.milestone_set.all()
    return render(request, 'timeline_app/project_detail.html', {
        'project': project,
        'milestones': milestones
    })

@login_required
def project_update(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('timeline_app:project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'timeline_app/project_form.html', {
        'form': form,
        'edit_mode': True,
        'project': project
    })

@login_required
def project_delete(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('timeline_app:dashboard')
    return render(request, 'timeline_app/project_confirm_delete.html', {
        'project': project
    })