# test_timeline_app.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from timeline_app.models import Project, Milestone
from datetime import datetime, timedelta

class TimelineAppTests(TestCase):
    def setUp(self):
        # Create test user
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create test project
        self.project = Project.objects.create(
            name='Test Project',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=30)).date(),
            user=self.user
        )

    def test_project_creation(self):
        """Test project creation functionality"""
        project_data = {
            'name': 'New Project',
            'start_date': '2025-02-01',
            'end_date': '2025-03-01'
        }
        response = self.client.post(reverse('project_create'), project_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Project.objects.filter(name='New Project').exists())

    def test_project_update(self):
        """Test project update functionality"""
        update_data = {
            'name': 'Updated Project',
            'start_date': '2025-02-01',
            'end_date': '2025-03-01'
        }
        response = self.client.post(
            reverse('project_update', kwargs={'project_id': self.project.id}),
            update_data
        )
        self.assertEqual(response.status_code, 302)
        updated_project = Project.objects.get(id=self.project.id)
        self.assertEqual(updated_project.name, 'Updated Project')

    def test_project_delete(self):
        """Test project deletion"""
        response = self.client.post(
            reverse('project_delete', kwargs={'project_id': self.project.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_milestone_creation(self):
        """Test milestone creation"""
        milestone_data = {
            'name': 'Test Milestone',
            'due_date': '2025-02-15'
        }
        response = self.client.post(
            reverse('milestone_create', kwargs={'project_id': self.project.id}),
            milestone_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Milestone.objects.filter(name='Test Milestone').exists())

    def test_dashboard_view(self):
        """Test dashboard view and timeline"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'timeline_app/dashboard.html')
        self.assertContains(response, self.project.name)