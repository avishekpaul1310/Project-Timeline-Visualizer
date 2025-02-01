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
        
        # Create test project
        self.project = Project.objects.create(
            name='Test Project',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=30)).date(),
            user=self.user
        )

    def test_login_required(self):
        """Test that login is required for protected pages"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_project_list(self):
        """Test project listing for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_project_create(self):
        """Test project creation"""
        self.client.login(username='testuser', password='testpass123')
        project_data = {
            'name': 'New Project',
            'start_date': '2025-02-01',
            'end_date': '2025-03-01'
        }
        response = self.client.post(reverse('project_create'), project_data)
        self.assertEqual(response.status_code, 302)  # Should redirect after creation
        self.assertTrue(Project.objects.filter(name='New Project').exists())

    def test_project_update(self):
        """Test project update"""
        self.client.login(username='testuser', password='testpass123')
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