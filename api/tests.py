from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Task


class TaskModelTest(TestCase):
    """Test suite for the Task model"""
    
    def setUp(self):
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            completed=False
        )
    
    def test_task_creation(self):
        """Test that a task can be created"""
        self.assertEqual(self.task.title, "Test Task")
        self.assertEqual(self.task.description, "Test Description")
        self.assertFalse(self.task.completed)
        
    def test_task_str(self):
        """Test the string representation of a task"""
        self.assertEqual(str(self.task), "Test Task")


class TaskAPITest(APITestCase):
    """Test suite for the Task API"""
    
    def setUp(self):
        self.task_data = {
            'title': 'New Task',
            'description': 'New Description',
            'completed': False
        }
        self.task = Task.objects.create(
            title="Existing Task",
            description="Existing Description"
        )
        
    def test_create_task(self):
        """Test creating a new task via API"""
        url = reverse('task-list')
        response = self.client.post(url, self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        payload = response.data.get('results', response.data)
        # When paginated, response is a dict; on create it's the object itself
        if isinstance(payload, dict) and 'title' in payload:
            self.assertEqual(payload['title'], 'New Task')
        else:
            self.assertEqual(response.data['title'], 'New Task')
        
    def test_get_task_list(self):
        """Test retrieving the list of tasks"""
        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Support paginated and non-paginated responses
        if isinstance(response.data, dict) and 'results' in response.data:
            self.assertEqual(response.data['count'], 1)
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)
        
    def test_get_task_detail(self):
        """Test retrieving a single task"""
        url = reverse('task-detail', args=[self.task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Existing Task')
        
    def test_update_task(self):
        """Test updating a task"""
        url = reverse('task-detail', args=[self.task.id])
        updated_data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
            'completed': True
        }
        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
        self.assertTrue(self.task.completed)
        
    def test_delete_task(self):
        """Test deleting a task"""
        url = reverse('task-detail', args=[self.task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)
