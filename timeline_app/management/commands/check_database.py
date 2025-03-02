from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from timeline_app.models import Project, Milestone
from django.db.models import Count

class Command(BaseCommand):
    help = 'Check for database inconsistencies related to projects and collaborators'

    def handle(self, *args, **options):
        self.stdout.write('Checking for database inconsistencies...')
        
        # Check for users
        users = User.objects.all()
        self.stdout.write(f'Total users: {users.count()}')
        for user in users:
            self.stdout.write(f'User: {user.username}, ID: {user.id}, Email: {user.email}')
        
        # Check for projects
        projects = Project.objects.all()
        self.stdout.write(f'Total projects: {projects.count()}')
        for project in projects:
            self.stdout.write(f'Project: {project.id} - {project.name}, Owner: {project.user.username} (ID: {project.user.id})')
            
            # List collaborators
            collab_count = project.collaborators.count()
            self.stdout.write(f'  Collaborators ({collab_count}):')
            for collaborator in project.collaborators.all():
                self.stdout.write(f'    {collaborator.username} (ID: {collaborator.id})')
                
            # Check if owner is also a collaborator (which could cause duplicates)
            if project.user in project.collaborators.all():
                self.stdout.write(self.style.WARNING(f'  WARNING: Owner is also listed as a collaborator!'))
        
        # Check for projects where a user is both owner and collaborator
        self.stdout.write('\nChecking for users who are both owner and collaborator of the same project:')
        for user in users:
            owned_projects = Project.objects.filter(user=user)
            for project in owned_projects:
                if user in project.collaborators.all():
                    self.stdout.write(self.style.WARNING(
                        f'User {user.username} is both owner and collaborator for project "{project.name}" (ID: {project.id})'
                    ))
                    
        # Check for duplicate collaborator entries
        self.stdout.write('\nChecking for duplicate collaborator entries:')
        for project in projects:
            # Count occurrences of each collaborator
            collab_counts = project.collaborators.values('id').annotate(count=Count('id')).filter(count__gt=1)
            if collab_counts.exists():
                for entry in collab_counts:
                    user_id = entry['id']
                    count = entry['count']
                    user = User.objects.get(id=user_id)
                    self.stdout.write(self.style.WARNING(
                        f'Project "{project.name}" (ID: {project.id}) has user {user.username} listed {count} times as a collaborator!'
                    ))
                    
        self.stdout.write(self.style.SUCCESS('Database check complete!'))