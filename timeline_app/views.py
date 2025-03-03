from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Milestone, Notification
from .forms import ProjectForm, MilestoneForm, ProjectShareForm
import json
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from .utils import check_upcoming_milestones
from django.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@login_required
def dashboard(request):
    try:
        # Get projects owned by the user
        owned_projects = Project.objects.filter(
            user=request.user, 
            is_archived=False
        )
        print(f"User {request.user.username} has {owned_projects.count()} owned projects")
        
        # Get projects shared with the user (where user is a collaborator)
        shared_projects = Project.objects.filter(
            collaborators=request.user,
            is_archived=False
        ).exclude(
            user=request.user  # Exclude projects where user is also the owner
        )
        print(f"User {request.user.username} has {shared_projects.count()} shared projects")
        
        # Combine the querysets
        all_projects = list(owned_projects) + list(shared_projects)
        print(f"Total projects for user {request.user.username}: {len(all_projects)}")
        
        # Create data for timeline
        projects_list = []
        for p in all_projects:
            print(f"Adding project to list: {p.id} - {p.name} - Owner: {p.user.username}")
            projects_list.append({
                'name': p.name,
                'start_date': p.start_date.strftime('%Y-%m-%d'),
                'end_date': p.end_date.strftime('%Y-%m-%d'),
                'id': p.id
            })
        
        # Sort by start date
        projects_list.sort(key=lambda x: x['start_date'])
        
        # Convert to JSON
        json_data = json.dumps(projects_list)
        
    except Exception as e:
        print(f"Error in dashboard: {e}")
        messages.error(request, "An error occurred while loading your projects.")
        all_projects = []
        json_data = "[]"
    
    return render(request, 'timeline_app/dashboard.html', {
        'projects': all_projects,
        'projects_json': json_data
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
def project_detail(request, project_id):
    try:
        # First try to get the project by ID
        project = Project.objects.get(id=project_id)
        
        # Check if the user has permission (is owner or collaborator)
        if project.user != request.user and request.user not in project.collaborators.all():
            messages.error(request, "You don't have permission to view this project.")
            return redirect('timeline_app:dashboard')
        
        # Fetch milestones
        milestones = Milestone.objects.filter(project=project)
        
        # Add a flag to indicate if the current user is the owner
        is_owner = (project.user == request.user)
        
    except Project.DoesNotExist:
        messages.error(request, "Project not found.")
        return redirect('timeline_app:dashboard')
    except Exception as e:
        print(f"Error in project_detail: {e}")
        messages.error(request, "An error occurred while loading the project.")
        return redirect('timeline_app:dashboard')
    
    return render(request, 'timeline_app/project_detail.html', {
        'project': project,
        'milestones': milestones,
        'is_owner': is_owner
    })

@login_required
def milestone_create(request, project_id):
    try:
        # Get the project by ID
        project = Project.objects.get(id=project_id)
        
        # Check if the user is the owner
        if project.user != request.user:
            messages.error(request, "Only the project owner can add milestones to this project.")
            return redirect('timeline_app:project_detail', project_id=project.id)
        
        if request.method == 'POST':
            form = MilestoneForm(request.POST, project=project)
            if form.is_valid():
                milestone = form.save(commit=False)
                milestone.project = project
                milestone.save()
                
                # Notify collaborators about the new milestone
                for collaborator in project.collaborators.all():
                    Notification.objects.create(
                        user=collaborator,
                        notification_type='milestone_added',
                        message=f"{request.user.username} added milestone '{milestone.name}' to project '{project.name}'",
                        project=project,
                        milestone=milestone
                    )
                
                messages.success(request, 'Milestone added successfully!')
                return redirect('timeline_app:project_detail', project_id=project.id)
        else:
            form = MilestoneForm(project=project)
    
    except Project.DoesNotExist:
        messages.error(request, "Project not found.")
        return redirect('timeline_app:dashboard')
    except Exception as e:
        print(f"Error in milestone_create: {e}")
        messages.error(request, "An error occurred while adding the milestone.")
        return redirect('timeline_app:dashboard')
    
    return render(request, 'timeline_app/milestone_form.html', {
        'form': form,
        'project': project
    })

@login_required
def project_update(request, project_id):
    try:
        # First try to get the project by ID
        project = Project.objects.get(id=project_id)
        
        # Check if the user is the owner
        if project.user != request.user:
            messages.error(request, "You don't have permission to edit this project. Only the project owner can make changes.")
            return redirect('timeline_app:project_detail', project_id=project.id)
            
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
        
    except Project.DoesNotExist:
        messages.error(request, "Project not found.")
        return redirect('timeline_app:dashboard')
    except Exception as e:
        print(f"Error in project_update view: {e}")
        messages.error(request, "An error occurred while trying to update the project.")
        return redirect('timeline_app:dashboard')

@login_required
def project_delete(request, project_id):
    try:
        # First try to get the project by ID
        project = Project.objects.get(id=project_id)
        
        # Check if the user is the owner
        if project.user != request.user:
            messages.error(request, "You don't have permission to delete this project. Only the project owner can delete it.")
            return redirect('timeline_app:project_detail', project_id=project.id)
            
        if request.method == 'POST':
            project.delete()
            messages.success(request, 'Project deleted successfully!')
            return redirect('timeline_app:dashboard')
            
        return render(request, 'timeline_app/project_confirm_delete.html', {
            'project': project
        })
        
    except Project.DoesNotExist:
        messages.error(request, "Project not found.")
        return redirect('timeline_app:dashboard')
    except Exception as e:
        print(f"Error in project_delete view: {e}")
        messages.error(request, "An error occurred while trying to delete the project.")
        return redirect('timeline_app:dashboard')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def share_project(request, project_id):
    try:
        # Get the project by ID
        project = Project.objects.get(id=project_id)
        
        # Check if the user is the owner
        if project.user != request.user:
            messages.error(request, "Only the project owner can share this project with others.")
            return redirect('timeline_app:project_detail', project_id=project.id)
        
        if request.method == 'POST':
            form = ProjectShareForm(request.POST)
            if form.is_valid():
                collaborator_email = form.cleaned_data['email']
                
                try:
                    # Get the user with this email
                    collaborator = User.objects.get(email=collaborator_email)
                    
                    # Check if user is already a collaborator
                    if collaborator == request.user:
                        messages.warning(request, "You can't add yourself as a collaborator.")
                    elif collaborator in project.collaborators.all():
                        messages.info(request, f"{collaborator.username} is already a collaborator.")
                    else:
                        # Add the collaborator to the project
                        project.collaborators.add(collaborator)
                        messages.success(request, f"Project shared with {collaborator.username} successfully!")
                        
                        # Create a notification for the collaborator
                        notification = Notification.objects.create(
                            user=collaborator,
                            notification_type='project_shared', 
                            message=f"{request.user.username} has shared the project '{project.name}' with you",
                            project=project
                        )
                        
                        # Send email notification
                        subject = f"{request.user.username} shared a project with you: {project.name}"

                        # Get the site's domain
                        site_domain = request.get_host()
                        
                        # Create email context
                        context = {
                            'username': collaborator.username,
                            'shared_by': request.user.username,
                            'project_name': project.name,
                            'login_url': f"http://{site_domain}/accounts/login/"
                        }

                        # Render HTML content
                        html_message = render_to_string('timeline_app/email/project_shared.html', context)
                        plain_message = strip_tags(html_message)

                        # Send email
                        try:
                            send_mail(
                                subject=subject,
                                message=plain_message,
                                from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
                                recipient_list=[collaborator.email],
                                html_message=html_message,
                                fail_silently=False
                            )
                        except Exception as e:
                            print(f"Error sending email: {e}")
                    
                    return redirect('timeline_app:project_detail', project_id=project.id)
                    
                except User.DoesNotExist:
                    messages.error(request, "No user with this email address was found.")
        else:
            form = ProjectShareForm()
        
        current_collaborators = project.collaborators.all()
        return render(request, 'timeline_app/share_project.html', {
            'form': form,
            'project': project,
            'current_collaborators': current_collaborators
        })
    
    except Project.DoesNotExist:
        messages.error(request, "Project not found.")
        return redirect('timeline_app:dashboard')
    except Exception as e:
        print(f"Error in share_project view: {e}")
        messages.error(request, "An error occurred while trying to share the project.")
        return redirect('timeline_app:dashboard')

@login_required
def remove_collaborator(request, project_id, user_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    collaborator = get_object_or_404(User, id=user_id)
    
    if collaborator in project.collaborators.all():
        project.collaborators.remove(collaborator)
        messages.success(request, f"{collaborator.username} removed from collaborators.")
    
    return redirect('timeline_app:share_project', project_id=project.id)

@login_required
def export_project(request, project_id, format_type):
    # Get the base project by ID
    project = get_object_or_404(Project, id=project_id)
    
    # Check if the user has permission to export this project
    if project.user != request.user and request.user not in project.collaborators.all():
        messages.error(request, "You don't have permission to export this project.")
        return redirect('timeline_app:dashboard')
    
    if format_type == 'csv':
        from .utils import export_project_to_csv
        return export_project_to_csv(project)
    elif format_type == 'pdf':
        from .utils import export_project_to_pdf
        return export_project_to_pdf(request, project)
    else:
        messages.error(request, f"Unknown export format: {format_type}")
        return redirect('timeline_app:project_detail', project_id=project.id)

@login_required
def notifications(request):
    # Get all notifications for the current user
    print(f"Retrieving notifications for user: {request.user.username} (ID: {request.user.id})")
    
    user_notifications = Notification.objects.filter(user=request.user)
    print(f"Found {user_notifications.count()} notifications")
    
    # Print details of each notification for debugging
    for notif in user_notifications:
        print(f"Notification #{notif.id}: {notif.message} - for user {notif.user.username}")
    
    unread_count = user_notifications.filter(is_read=False).count()
    
    return render(request, 'timeline_app/notifications.html', {
        'notifications': user_notifications,
        'unread_count': unread_count
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if notification.project:
        return redirect('timeline_app:project_detail', project_id=notification.project.id)
    return redirect('timeline_app:notifications')

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect('timeline_app:notifications')

@login_required
def archive_project(request, project_id):
    try:
        # Get the project by ID
        project = Project.objects.get(id=project_id)
        
        # Check if the user is the owner
        if project.user != request.user:
            messages.error(request, "Only the project owner can archive this project.")
            return redirect('timeline_app:project_detail', project_id=project.id)
        
        project.is_archived = True
        project.save()
        messages.success(request, f"Project '{project.name}' has been archived.")
        return redirect('timeline_app:dashboard')
    
    except Project.DoesNotExist:
        messages.error(request, "Project not found.")
        return redirect('timeline_app:dashboard')
    except Exception as e:
        print(f"Error in archive_project: {e}")
        messages.error(request, "An error occurred while archiving the project.")
        return redirect('timeline_app:dashboard')

@login_required
def unarchive_project(request, project_id):
    try:
        # Get the project by ID
        project = Project.objects.get(id=project_id)
        
        # Check if the user is the owner
        if project.user != request.user:
            messages.error(request, "Only the project owner can unarchive this project.")
            return redirect('timeline_app:project_detail', project_id=project.id)
        
        project.is_archived = False
        project.save()
        messages.success(request, f"Project '{project.name}' has been unarchived.")
        return redirect('timeline_app:archived_projects')
    
    except Project.DoesNotExist:
        messages.error(request, "Project not found.")
        return redirect('timeline_app:dashboard')
    except Exception as e:
        print(f"Error in unarchive_project: {e}")
        messages.error(request, "An error occurred while unarchiving the project.")
        return redirect('timeline_app:dashboard')

@login_required
def archived_projects(request):
    archived_projects = Project.objects.filter(
        user=request.user, 
        is_archived=True
    )
    return render(request, 'timeline_app/archived_projects.html', {
        'archived_projects': archived_projects
    })

@login_required
def analytics(request):
    # Get user's projects (both owned and shared)
    owned_projects = Project.objects.filter(user=request.user)
    shared_projects = Project.objects.filter(collaborators=request.user)
    
    # Use a dictionary to prevent duplicates
    project_dict = {p.id: p for p in owned_projects}
    for p in shared_projects:
        if p.id not in project_dict:
            project_dict[p.id] = p
            
    all_projects = list(project_dict.values())
    
    # Basic statistics
    total_projects = len(all_projects)
    active_projects = sum(1 for p in all_projects if not p.is_archived)
    archived_projects = total_projects - active_projects
    
    # Milestones stats
    all_milestones = Milestone.objects.filter(project__in=all_projects)
    total_milestones = all_milestones.count()
    
    # Milestone completion stats
    completed_milestones = all_milestones.filter(status='completed').count()
    pending_milestones = all_milestones.filter(status='pending').count()
    in_progress_milestones = all_milestones.filter(status='in_progress').count()
    delayed_milestones = all_milestones.filter(status='delayed').count()
    
    # Calculate completion percentage
    completion_percentage = 0
    if total_milestones > 0:
        completion_percentage = round((completed_milestones / total_milestones) * 100)
    
    from django.utils import timezone
    today = timezone.now().date()
    
    # Calculate overdue milestones (due date in past but not completed)
    overdue_milestones = all_milestones.filter(
        due_date__lt=today,
        status__in=['pending', 'in_progress', 'delayed']
    ).count()
    
    # Regular milestone time stats
    upcoming_milestones = all_milestones.filter(due_date__gt=today).count()
    past_milestones = all_milestones.filter(due_date__lt=today).count()
    today_milestones = all_milestones.filter(due_date=today).count()
    
    # Project timeline data for chart
    from collections import defaultdict
    import calendar
    
    # Get project counts by month
    months_data = defaultdict(int)
    for project in all_projects:
        month_year = project.created_at.strftime('%Y-%m')
        months_data[month_year] += 1
    
    # Sort by date
    sorted_months = sorted(months_data.keys())
    month_labels = []
    month_counts = []
    
    for month_year in sorted_months:
        year, month = map(int, month_year.split('-'))
        month_name = calendar.month_name[month]
        month_labels.append(f"{month_name} {year}")
        month_counts.append(months_data[month_year])
    
    # Milestone completion rate
    milestone_completion = {
        'total': total_milestones,
        'upcoming': upcoming_milestones,
        'past': past_milestones,
        'today': today_milestones,
        'completed': completed_milestones,
        'pending': pending_milestones,
        'in_progress': in_progress_milestones,
        'delayed': delayed_milestones,
        'overdue': overdue_milestones,
        'completion_percentage': completion_percentage
    }
    
    # Get top 3 projects by number of milestones
    projects_by_milestones = []
    for project in all_projects:
        milestone_count = Milestone.objects.filter(project=project).count()
        projects_by_milestones.append({
            'id': project.id,
            'name': project.name,
            'milestone_count': milestone_count
        })
    
    # Sort by milestone count (descending)
    projects_by_milestones.sort(key=lambda x: x['milestone_count'], reverse=True)
    top_projects = projects_by_milestones[:3]  # Get top 3
    
    return render(request, 'timeline_app/analytics.html', {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'archived_projects': archived_projects,
        'milestone_stats': milestone_completion,
        'top_projects': top_projects,
        'month_labels': json.dumps(month_labels),
        'month_counts': json.dumps(month_counts),
    })

# Add this to your views.py file
@login_required
def project_diagnostic(request):
    """A diagnostic view to help troubleshoot project visibility issues"""
    user = request.user
    
    # Get all projects in the database
    all_projects_in_db = Project.objects.all()
    
    # Get projects where the user is the owner
    owned_projects = Project.objects.filter(user=user)
    
    # Get projects where the user is a collaborator
    shared_projects = Project.objects.filter(collaborators=user)
    
    # Get the combined projects as we're doing in the dashboard view
    from django.db.models import Q
    combined_projects = Project.objects.filter(
        Q(user=user) | Q(collaborators=user)
    ).distinct()
    
    # Create context
    context = {
        'username': user.username,
        'user_id': user.id,
        'all_projects_count': all_projects_in_db.count(),
        'all_projects': [
            {
                'id': p.id, 
                'name': p.name, 
                'owner': p.user.username,
                'owner_id': p.user.id,
                'collaborators': [c.username for c in p.collaborators.all()]
            } for p in all_projects_in_db
        ],
        'owned_projects_count': owned_projects.count(),
        'owned_projects': [
            {
                'id': p.id, 
                'name': p.name
            } for p in owned_projects
        ],
        'shared_projects_count': shared_projects.count(),
        'shared_projects': [
            {
                'id': p.id, 
                'name': p.name,
                'owner': p.user.username
            } for p in shared_projects
        ],
        'combined_projects_count': combined_projects.count(),
        'combined_projects': [
            {
                'id': p.id, 
                'name': p.name, 
                'owner': p.user.username
            } for p in combined_projects
        ]
    }
    
    return render(request, 'timeline_app/diagnostic.html', context)

# Then add a URL pattern in urls.py
# path('diagnostic/', views.project_diagnostic, name='project_diagnostic'),

# Create the diagnostic.html template in your templates folder
"""
{% extends 'timeline_app/base.html' %}

{% block content %}
<div class="card mb-4">
    <div class="card-header">
        <h2>Project Visibility Diagnostic</h2>
        <p>User: {{ username }} (ID: {{ user_id }})</p>
    </div>
    <div class="card-body">
        <h3>All Projects in Database ({{ all_projects_count }})</h3>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Owner</th>
                    <th>Owner ID</th>
                    <th>Collaborators</th>
                </tr>
            </thead>
            <tbody>
                {% for project in all_projects %}
                <tr>
                    <td>{{ project.id }}</td>
                    <td>{{ project.name }}</td>
                    <td>{{ project.owner }}</td>
                    <td>{{ project.owner_id }}</td>
                    <td>{{ project.collaborators|join:", " }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <h3>Owned Projects ({{ owned_projects_count }})</h3>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                </tr>
            </thead>
            <tbody>
                {% for project in owned_projects %}
                <tr>
                    <td>{{ project.id }}</td>
                    <td>{{ project.name }}</td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="2">No owned projects</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <h3>Shared Projects ({{ shared_projects_count }})</h3>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Owner</th>
                </tr>
            </thead>
            <tbody>
                {% for project in shared_projects %}
                <tr>
                    <td>{{ project.id }}</td>
                    <td>{{ project.name }}</td>
                    <td>{{ project.owner }}</td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="3">No shared projects</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <h3>Combined Projects ({{ combined_projects_count }})</h3>
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Owner</th>
                </tr>
            </thead>
            <tbody>
                {% for project in combined_projects %}
                <tr>
                    <td>{{ project.id }}</td>
                    <td>{{ project.name }}</td>
                    <td>{{ project.owner }}</td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="3">No combined projects</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
"""

@login_required
def milestone_update(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    project = milestone.project
    
    # Check if the user is the owner
    if project.user != request.user:
        messages.error(request, "Only the project owner can edit milestones.")
        return redirect('timeline_app:project_detail', project_id=project.id)
    
    if request.method == 'POST':
        form = MilestoneForm(request.POST, instance=milestone, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Milestone updated successfully!')
            return redirect('timeline_app:project_detail', project_id=project.id)
    else:
        form = MilestoneForm(instance=milestone, project=project)
    
    return render(request, 'timeline_app/milestone_form.html', {
        'form': form,
        'project': project,
        'edit_mode': True,
        'milestone': milestone
    })

@login_required
def update_milestone_status(request, milestone_id, status):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    project = milestone.project
    
    # Check if the user is the owner
    if project.user != request.user:
        messages.error(request, "Only the project owner can update milestone status.")
        return redirect('timeline_app:project_detail', project_id=project.id)
    
    # Validate the status
    valid_statuses = dict(Milestone.STATUS_CHOICES).keys()
    if status not in valid_statuses:
        messages.error(request, f"Invalid status: {status}")
        return redirect('timeline_app:project_detail', project_id=project.id)
    
    # Update the milestone status
    milestone.status = status
    milestone.save()
    
    messages.success(request, f"Milestone '{milestone.name}' status updated to {status.replace('_', ' ').title()}")
    return redirect('timeline_app:project_detail', project_id=project.id)