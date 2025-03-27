# Generated manually

from django.db import migrations

def initialize_milestone_start_dates(apps, schema_editor):
    """Set start_date equal to due_date for all existing milestones."""
    Milestone = apps.get_model('timeline_app', 'Milestone')
    for milestone in Milestone.objects.all():
        if not milestone.start_date:
            milestone.start_date = milestone.due_date
            milestone.save()

class Migration(migrations.Migration):

    dependencies = [
        ('timeline_app', '0004_milestone_dependencies_start_date_duration'),
    ]

    operations = [
        migrations.RunPython(initialize_milestone_start_dates),
    ]