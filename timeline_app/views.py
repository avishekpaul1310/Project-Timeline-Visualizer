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
    import json
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
                    
                    
                notification = Notification.objects.create(
                user=collaborator,  # This is the recipient user
                notification_type='project_shared', 
                message=f"{request.user.username} has shared the project '{project.name}' with you",
                project=project)

                print(f"Created notification ID {notification.id} for user {collaborator.username} (ID: {collaborator.id})")
                    
                    # Send email notification
                from django.core.mail import send_mail
                from django.template.loader import render_to_string
                from django.utils.html import strip_tags

                    # Email subject
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
def send_collaboration_notification(collaborator, project, from_user):
    
    Notification.objects.create(
        user=collaborator,
        notification_type='project_shared', 
        message=f"{from_user.username} has shared the project '{project.name}' with you",
        project=project
    )

def export_project_to_csv(project):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{project.name}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Project Name', 'Start Date', 'End Date', 'Description'])
    writer.writerow([project.name, project.start_date, project.end_date, project.description])
    
    writer.writerow([])  # Empty row for separation
    writer.writerow(['Milestone', 'Due Date', 'Description', 'Status'])
    
    for milestone in project.milestone_set.all():
        writer.writerow([milestone.title, milestone.due_date, milestone.description, milestone.status])
    
    return response

def export_project_to_pdf(request, project):
    from django.http import HttpResponse
    from django.template.loader import render_to_string
    from weasyprint import HTML
    import tempfile
    
    html_string = render_to_string('timeline_app/project_pdf_template.html', {
        'project': project,
        'milestones': project.milestone_set.all(),
    })
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{project.name}.pdf"'
    
    HTML(string=html_string).write_pdf(response)
    return response

@login_required
def notifications(request):
    # Get all notifications for the current user
    print(f"Retrieving notifications for user: {request.user.username} (ID: {request.user.id})")
    
    user_notifications = Notification.objects.filter(user=request.user)
    print(f"Found {user_notifications.count()} notifications")
    
    # Print details of each notification for debugging
    for notif in user_notifications:
        print(f"Notification #{notif.id}: {notif.message} - for user {notif.user.username}")
    
    # Check all notifications in the system
    all_notifs = Notification.objects.all()
    print(f"Total notifications in system: {all_notifs.count()}")
    for notif in all_notifs:
        print(f"System notification #{notif.id}: {notif.message} - for user {notif.user.username}")
    
    return render(request, 'timeline_app/notifications.html', {
        'notifications': user_notifications,
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
def export_project(request, project_id, format_type):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has access to this project
    if project.user != request.user and request.user not in project.collaborators.all():
        messages.error(request, "You don't have permission to export this project.")
        return redirect('timeline_app:dashboard')
    
    if format_type == 'csv':
        # Use the local version defined in this file
        return export_project_to_csv(project)
    elif format_type == 'pdf':
        # Use the local version defined in this file
        return export_project_to_pdf(request, project)
    else:
        messages.error(request, f"Unknown export format: {format_type}")
        return redirect('timeline_app:project_detail', project_id=project.id)

        
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