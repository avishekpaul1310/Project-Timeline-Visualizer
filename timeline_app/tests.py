from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from timeline_app.models import Project, Milestone
from datetime import datetime, timedelta
from django.utils import timezone

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
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=30)).date(),
            user=self.user
        )

        # Create test milestone
        self.milestone = Milestone.objects.create(
            name='Test Milestone',
            due_date=timezone.now().date() + timedelta(days=15),
            project=self.project
        )

    def test_login_required(self):
        """Test that login is required for protected pages"""
        urls = [
            reverse('timeline_app:dashboard'),
            reverse('timeline_app:project_create'),
            reverse('timeline_app:project_detail', kwargs={'project_id': self.project.id}),
            reverse('timeline_app:project_update', kwargs={'project_id': self.project.id}),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_project_list(self):
        """Test project listing for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('timeline_app:dashboard'))
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
        response = self.client.post(reverse('timeline_app:project_create'), project_data)
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
            reverse('timeline_app:project_update', kwargs={'project_id': self.project.id}),
            update_data
        )
        self.assertEqual(response.status_code, 302)
        updated_project = Project.objects.get(id=self.project.id)
        self.assertEqual(updated_project.name, 'Updated Project')

    def test_project_detail(self):
        """Test project detail view"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('timeline_app:project_detail', kwargs={'project_id': self.project.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertContains(response, 'Test Milestone')

    def test_project_delete(self):
        """Test project deletion"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('timeline_app:project_delete', kwargs={'project_id': self.project.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_milestone_create(self):
        """Test milestone creation"""
        self.client.login(username='testuser', password='testpass123')
        milestone_data = {
            'name': 'New Milestone',
            'due_date': (self.project.start_date + timedelta(days=15)).isoformat()
        }
        response = self.client.post(
            reverse('timeline_app:milestone_create', kwargs={'project_id': self.project.id}),
            milestone_data
        )
        self.assertEqual(response.status_code, 302)  # Should redirect after creation
        self.assertTrue(Milestone.objects.filter(name='New Milestone').exists())
    def test_invalid_date_range(self):
        """Test validation for invalid date ranges"""
        self.client.login(username='testuser', password='testpass123')
        project_data = {
            'name': 'Invalid Project',
            'start_date': '2025-03-01',  # Start date after end date
            'end_date': '2025-02-01'
        }
        response = self.client.post(
            reverse('timeline_app:project_create'),
            project_data,
            follow=True  # Follow the redirect
        )
        self.assertEqual(response.status_code, 200)  # Should stay on form
        self.assertFalse(Project.objects.filter(name='Invalid Project').exists())
        self.assertContains(response, "End date cannot be before start date")