# timeline_app/management/commands/check_milestones.py
from django.core.management.base import BaseCommand
from timeline_app.utils import check_upcoming_milestones

class Command(BaseCommand):
    help = 'Check for upcoming milestones and create notifications'

    def handle(self, *args, **options):
        check_upcoming_milestones()
        self.stdout.write(self.style.SUCCESS('Successfully checked milestones'))