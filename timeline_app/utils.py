# timeline_app/utils.py
from datetime import datetime, timedelta
from .models import Milestone, Notification
import csv
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template

def check_upcoming_milestones():
    """Check for milestones due within the next 3 days and create notifications"""
    today = datetime.now().date()
    three_days_from_now = today + timedelta(days=3)
    
    # Find milestones due within the next 3 days
    upcoming_milestones = Milestone.objects.filter(
        due_date__range=[today, three_days_from_now]
    )
    
    for milestone in upcoming_milestones:
        # Create notification for the project owner
        owner = milestone.project.user
        days_left = (milestone.due_date - today).days
        
        # Check if notification already exists
        if not Notification.objects.filter(
            user=owner,
            notification_type='milestone_due',
            milestone=milestone,
            is_read=False
        ).exists():
            Notification.objects.create(
                user=owner,
                notification_type='milestone_due',
                project=milestone.project,
                milestone=milestone,
                message=f"Milestone '{milestone.name}' is due in {days_left} days."
            )
        
        # Create notifications for collaborators
        for collaborator in milestone.project.collaborators.all():
            if not Notification.objects.filter(
                user=collaborator,
                notification_type='milestone_due',
                milestone=milestone,
                is_read=False
            ).exists():
                Notification.objects.create(
                    user=collaborator,
                    notification_type='milestone_due',
                    project=milestone.project,
                    milestone=milestone,
                    message=f"Milestone '{milestone.name}' is due in {days_left} days."
                )

def export_project_to_csv(project):
    """Export project details to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{project.name}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Project Name', 'Start Date', 'End Date', 'Owner', 'Created At'])
    writer.writerow([
        project.name, 
        project.start_date, 
        project.end_date, 
        project.user.username,
        project.created_at
    ])
    
    writer.writerow([])  # Empty row
    writer.writerow(['Milestones'])
    writer.writerow(['Name', 'Due Date'])
    
    for milestone in project.milestone_set.all():
        writer.writerow([milestone.name, milestone.due_date])
    
    return response

def export_project_to_pdf(request, project):
    """Placeholder for PDF export functionality"""
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{project.name}.txt"'
    response.write(f"Project: {project.name}\n")
    response.write(f"Date Range: {project.start_date} to {project.end_date}\n")
    response.write(f"Owner: {project.user.username}\n\n")
    response.write("Milestones:\n")
    for milestone in project.milestone_set.all():
        response.write(f"- {milestone.name}: {milestone.due_date}\n")
    return response