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
    # Get active projects (not archived)
    owned_projects = Project.objects.filter(user=request.user, is_archived=False)
    shared_projects = Project.objects.filter(collaborators=request.user, is_archived=False)
    
    # Combine owned and shared projects without duplicates
    project_ids = set()
    all_projects = []
    
    for p in owned_projects:
        if p.id not in project_ids:
            all_projects.append(p)
            project_ids.add(p.id)
    
    for p in shared_projects:
        if p.id not in project_ids:
            all_projects.append(p)
            project_ids.add(p.id)
    
    # Create a list of project data for the timeline
    projects_list = []
    for p in all_projects:
        # Ensure dates are properly formatted for JavaScript
        projects_list.append({
            'name': p.name,
            'start_date': p.start_date.strftime('%Y-%m-%d'),  # Use consistent format
            'end_date': p.end_date.strftime('%Y-%m-%d'),      # Use consistent format
            'id': p.id
        })
    
    # Sort projects by start date for better display
    projects_list.sort(key=lambda x: x['start_date'])
    
    # Convert to JSON
    json_data = json.dumps(projects_list)
    
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
    # Get the project if the user is either the owner or a collaborator
    project_queryset = Project.objects.filter(id=project_id).filter(
        models.Q(user=request.user) | models.Q(collaborators=request.user)
    )
    
    project = get_object_or_404(project_queryset)
    milestones = project.milestone_set.all()
    
    # Add a flag to indicate if the current user is the owner
    is_owner = (project.user == request.user)
    
    return render(request, 'timeline_app/project_detail.html', {
        'project': project,
        'milestones': milestones,
        'is_owner': is_owner  # Pass this to the template
    })

@login_required
def milestone_create(request, project_id):
    # Allow both owner and collaborators to add milestones
    project_queryset = Project.objects.filter(id=project_id).filter(
        models.Q(user=request.user) | models.Q(collaborators=request.user)
    )
    
    project = get_object_or_404(project_queryset)
    
    if request.method == 'POST':
        form = MilestoneForm(request.POST, project=project)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()
            
            # Notify the project owner if a collaborator added a milestone
            if project.user != request.user:
                Notification.objects.create(
                    user=project.user,
                    notification_type='milestone_added',
                    message=f"{request.user.username} added milestone '{milestone.name}' to your project '{project.name}'",
                    project=project,
                    milestone=milestone
                )
            
            messages.success(request, 'Milestone added successfully!')
            return redirect('timeline_app:project_detail', project_id=project.id)
    else:
        form = MilestoneForm(project=project)
    
    return render(request, 'timeline_app/milestone_form.html', {
        'form': form,
        'project': project
    })

@login_required
def project_update(request, project_id):
    # Only the owner can update the project
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

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def share_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    
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
                    
                    print(f"Created notification ID {notification.id} for user {collaborator.username} (ID: {collaborator.id})")
                    
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
                        print(f"Email sent to {collaborator.email}")
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
    # Allow both owner and collaborators to export projects
    # Using filter first, then get_object_or_404 on the filtered queryset
    project_queryset = Project.objects.filter(
        id=project_id
    ).filter(
        models.Q(user=request.user) | models.Q(collaborators=request.user)
    )
    
    project = get_object_or_404(project_queryset)
    
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
    project = get_object_or_404(Project, id=project_id, user=request.user)
    project.is_archived = True
    project.save()
    messages.success(request, f"Project '{project.name}' has been archived.")
    return redirect('timeline_app:dashboard')

@login_required
def unarchive_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user=request.user)
    project.is_archived = False
    project.save()
    messages.success(request, f"Project '{project.name}' has been unarchived.")
    return redirect('timeline_app:archived_projects')

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
    
    from django.utils import timezone
    today = timezone.now().date()
    
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
    }
    
    return render(request, 'timeline_app/analytics.html', {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'archived_projects': archived_projects,
        'milestone_stats': milestone_completion,
        'month_labels': json.dumps(month_labels),
        'month_counts': json.dumps(month_counts),
    })