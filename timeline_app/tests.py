from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from timeline_app.models import Project, Milestone, Notification
from datetime import datetime, timedelta
from django.utils import timezone
import json

class TimelineAppBaseTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.collaborator = User.objects.create_user(
            username='collaborator',
            email='collaborator@example.com',
            password='collabpass123'
        )
        
        # Create test project with specific dates
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

class AuthenticationTests(TimelineAppBaseTestCase):
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
            self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_login_successful(self):
        """Test successful login redirects to dashboard"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('timeline_app:dashboard'))

    def test_logout_successful(self):
        """Test successful logout redirects to login page"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

class ProjectCRUDTests(TimelineAppBaseTestCase):
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
        
class MilestoneTests(TimelineAppBaseTestCase):
    def test_milestone_create(self):
        """Test milestone creation"""
        self.client.login(username='testuser', password='testpass123')
        
        # Calculate a valid due date within the project's timeframe
        valid_due_date = self.project.start_date + timedelta(days=15)
        
        milestone_data = {
            'name': 'New Milestone',
            'due_date': valid_due_date.isoformat(),
            'status': 'pending',
            'description': 'Test milestone description'
        }
        
        response = self.client.post(
            reverse('timeline_app:milestone_create', kwargs={'project_id': self.project.id}), 
            milestone_data
        )
        
        self.assertEqual(response.status_code, 302)  # Should redirect after creation
        
        # Verify the milestone was created with correct project association
        milestone = Milestone.objects.filter(name='New Milestone').first()
        self.assertIsNotNone(milestone)
        self.assertEqual(milestone.project, self.project)
        self.assertEqual(milestone.due_date, valid_due_date)
        self.assertEqual(milestone.description, 'Test milestone description')
    
    def test_milestone_update(self):
        """Test milestone update"""
        self.client.login(username='testuser', password='testpass123')
        
        update_data = {
            'name': 'Updated Milestone',
            'due_date': self.milestone.due_date.isoformat(),
            'status': 'in_progress',
            'description': 'Updated description'
        }
        
        response = self.client.post(
            reverse('timeline_app:milestone_update', kwargs={'milestone_id': self.milestone.id}),
            update_data
        )
        
        self.assertEqual(response.status_code, 302)
        updated_milestone = Milestone.objects.get(id=self.milestone.id)
        self.assertEqual(updated_milestone.name, 'Updated Milestone')
        self.assertEqual(updated_milestone.status, 'in_progress')
    
    def test_update_milestone_status(self):
        """Test updating milestone status"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('timeline_app:update_milestone_status', 
                   kwargs={'milestone_id': self.milestone.id, 'status': 'completed'})
        )
        
        self.assertEqual(response.status_code, 302)
        updated_milestone = Milestone.objects.get(id=self.milestone.id)
        self.assertEqual(updated_milestone.status, 'completed')

class CollaborationTests(TimelineAppBaseTestCase):
    def test_share_project(self):
        """Test sharing a project with another user"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('timeline_app:share_project', kwargs={'project_id': self.project.id}),
            {'email': 'collaborator@example.com'}
        )
        
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertIn(self.collaborator, self.project.collaborators.all())
        
        # Check if notification was created
        self.assertTrue(
            Notification.objects.filter(
                user=self.collaborator,
                notification_type='project_shared',
                project=self.project
            ).exists()
        )
    
    def test_collaborator_can_view_project(self):
        """Test that collaborators can view shared projects"""
        # Add collaborator to project
        self.project.collaborators.add(self.collaborator)
        
        # Login as collaborator
        self.client.login(username='collaborator', password='collabpass123')
        
        # Try to access the project
        response = self.client.get(
            reverse('timeline_app:project_detail', kwargs={'project_id': self.project.id})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
    
    def test_collaborator_cannot_edit_project(self):
        """Test that collaborators cannot edit projects"""
        # Add collaborator to project
        self.project.collaborators.add(self.collaborator)
        
        # Login as collaborator
        self.client.login(username='collaborator', password='collabpass123')
        
        # Try to edit the project
        update_data = {
            'name': 'Collaborator Updated',
            'start_date': '2025-02-01',
            'end_date': '2025-03-01'
        }
        
        response = self.client.post(
            reverse('timeline_app:project_update', kwargs={'project_id': self.project.id}),
            update_data,
            follow=True
        )
        
        # Should see access denied message - checking for partial text to be more robust
        self.assertContains(response, "You don't have permission to edit this project")
        
        # Project name should not be updated
        self.project.refresh_from_db()
        self.assertNotEqual(self.project.name, 'Collaborator Updated')
    
    def test_remove_collaborator(self):
        """Test removing a collaborator from a project"""
        # Add collaborator to project
        self.project.collaborators.add(self.collaborator)
        
        # Login as project owner
        self.client.login(username='testuser', password='testpass123')
        
        # Remove collaborator
        response = self.client.get(
            reverse('timeline_app:remove_collaborator', 
                   kwargs={'project_id': self.project.id, 'user_id': self.collaborator.id})
        )
        
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertNotIn(self.collaborator, self.project.collaborators.all())

class NotificationTests(TimelineAppBaseTestCase):
    def test_milestone_due_notification(self):
        """Test notification creation for upcoming milestones"""
        from timeline_app.utils import check_upcoming_milestones
        
        # Set milestone due date to tomorrow
        tomorrow = timezone.now().date() + timedelta(days=1)
        self.milestone.due_date = tomorrow
        self.milestone.save()
        
        # Run the notification check
        check_upcoming_milestones()
        
        # Check if notification was created
        self.assertTrue(
            Notification.objects.filter(
                user=self.user,
                notification_type='milestone_due',
                milestone=self.milestone
            ).exists()
        )
    
    def test_mark_notification_read(self):
        """Test marking a notification as read"""
        # Create a notification
        notification = Notification.objects.create(
            user=self.user,
            notification_type='milestone_due',
            project=self.project,
            milestone=self.milestone,
            message='Test notification',
            is_read=False
        )
        
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Mark as read
        response = self.client.get(
            reverse('timeline_app:mark_notification_read', kwargs={'notification_id': notification.id})
        )
        
        self.assertEqual(response.status_code, 302)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
    
    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        # Create multiple notifications
        for i in range(3):
            Notification.objects.create(
                user=self.user,
                notification_type='milestone_due',
                project=self.project,
                milestone=self.milestone,
                message=f'Test notification {i+1}',
                is_read=False
            )
        
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Mark all as read
        response = self.client.get(reverse('timeline_app:mark_all_read'))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Notification.objects.filter(user=self.user, is_read=False).count(), 0)

class AnalyticsTests(TimelineAppBaseTestCase):
    def test_analytics_view(self):
        """Test analytics view displays correctly"""
        # Create more milestones with different statuses
        Milestone.objects.create(
            name='Completed Milestone',
            due_date=timezone.now().date() + timedelta(days=5),
            project=self.project,
            status='completed'
        )
        
        Milestone.objects.create(
            name='In Progress Milestone',
            due_date=timezone.now().date() + timedelta(days=10),
            project=self.project,
            status='in_progress'
        )
        
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Access analytics page
        response = self.client.get(reverse('timeline_app:analytics'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Project Analytics')
        
        # Check that milestone stats are included
        self.assertContains(response, 'Milestone Completion Rate')
        self.assertContains(response, 'Milestone Status')

class ArchiveTests(TimelineAppBaseTestCase):
    def test_archive_project(self):
        """Test archiving a project"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('timeline_app:archive_project', kwargs={'project_id': self.project.id})
        )
        
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertTrue(self.project.is_archived)
        
        # Project should appear in archived projects list
        response = self.client.get(reverse('timeline_app:archived_projects'))
        self.assertContains(response, 'Test Project')
        
        # Project should not appear in dashboard
        response = self.client.get(reverse('timeline_app:dashboard'))
        self.assertNotContains(response, 'Test Project')
    
    def test_unarchive_project(self):
        """Test unarchiving a project"""
        # Archive project first
        self.project.is_archived = True
        self.project.save()
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('timeline_app:unarchive_project', kwargs={'project_id': self.project.id})
        )
        
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertFalse(self.project.is_archived)
        
        # Project should appear in dashboard
        response = self.client.get(reverse('timeline_app:dashboard'))
        self.assertContains(response, 'Test Project')

class ExportTests(TimelineAppBaseTestCase):
    def test_export_project_as_csv(self):
        """Test exporting a project as CSV"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('timeline_app:export_project', 
                   kwargs={'project_id': self.project.id, 'format_type': 'csv'})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue('attachment; filename=' in response['Content-Disposition'])
        
        # Check CSV content
        content = response.content.decode('utf-8')
        self.assertIn('Test Project', content)
        self.assertIn('Test Milestone', content)
    
    def test_export_project_as_pdf(self):
        """Test exporting a project as PDF"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(
            reverse('timeline_app:export_project', 
                   kwargs={'project_id': self.project.id, 'format_type': 'pdf'})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue('attachment; filename=' in response['Content-Disposition'])
        
class SecurityAndPermissionTests(TimelineAppBaseTestCase):
    def test_unauthorized_project_access(self):
        """Test unauthorized access to project"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='otherpass123'
        )
        
        # Login as the other user
        self.client.login(username='otheruser', password='otherpass123')
        
        # Try to access project
        response = self.client.get(
            reverse('timeline_app:project_detail', kwargs={'project_id': self.project.id}),
            follow=True
        )
        
        # Check for the presence of the error message without requiring exact matching
        self.assertContains(response, "You don't have permission to view this project")
    
    def test_unauthorized_milestone_creation(self):
        """Test that only project owner can create milestones"""
        # Add collaborator to project
        self.project.collaborators.add(self.collaborator)
        
        # Login as collaborator
        self.client.login(username='collaborator', password='collabpass123')
        
        # Try to create milestone
        milestone_data = {
            'name': 'Unauthorized Milestone',
            'due_date': (timezone.now().date() + timedelta(days=5)).isoformat(),
            'status': 'pending',
            'description': 'Test milestone'
        }
        
        response = self.client.post(
            reverse('timeline_app:milestone_create', kwargs={'project_id': self.project.id}),
            milestone_data,
            follow=True
        )
        
        # Should be redirected with error message
        self.assertContains(response, "Only the project owner can add milestones to this project")
        
        # Milestone should not be created
        self.assertFalse(Milestone.objects.filter(name='Unauthorized Milestone').exists())