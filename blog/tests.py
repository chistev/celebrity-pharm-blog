import json
import unittest
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post, Category, Subscriber
from django.utils import timezone

class BlogIndexViewTests(TestCase):
    def setUp(self):
        # Set up test client
        self.client = Client()
        
        # Create a test category
        self.category = Category.objects.create(
            title="Test Category",
            description="Test Description",
            image="category_images/test.jpg",
            slug="test-category"
        )
        
        # Create test posts
        self.post1 = Post.objects.create(
            title="Test Post 1",
            excerpt="Test excerpt 1",
            image="post_images/test1.jpg",
            slug="test-post-1",
            category=self.category,
            content="Test content 1",
            status="published",
            created_at=timezone.now()
        )
        self.post2 = Post.objects.create(
            title="Test Post 2",
            excerpt="Test excerpt 2",
            image="post_images/test2.jpg",
            slug="test-post-2",
            category=self.category,
            content="Test content 2",
            status="published",
            created_at=timezone.now()
        )

    def test_blog_index_hx_request_happy_path(self):
        """
        Happy Path: Test that HX-Request header returns the partial template.
        """
        # Simulate a request with HX-Request header
        response = self.client.get(
            reverse('index'),
            HTTP_HX_REQUEST='true'
        )
        
        # Assert the correct template is used
        self.assertTemplateUsed(response, 'blog/partials/post_list.html')
        
        # Assert the response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Assert the context contains 'posts'
        self.assertIn('posts', response.context)
        
        # Assert the posts are paginated correctly (4 posts per page)
        self.assertEqual(len(response.context['posts']), 2)  # Only 2 posts created
        
        # Assert the response content contains post titles
        self.assertContains(response, "Test Post 1")
        self.assertContains(response, "Test Post 2")

    def test_blog_index_no_hx_request_unhappy_path(self):
        """
        Unhappy Path: Test that no HX-Request header returns the full index template.
        """
        # Simulate a request without HX-Request header
        response = self.client.get(reverse('index'))
        
        # Assert the full index template is used
        self.assertTemplateUsed(response, 'blog/index.html')
        
        # Assert the response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Assert the context contains 'posts', 'categories', and 'subscriber_count'
        self.assertIn('posts', response.context)
        self.assertIn('categories', response.context)
        self.assertIn('subscriber_count', response.context)
        
        # Assert the posts are paginated correctly
        self.assertEqual(len(response.context['posts']), 2)  # Only 2 posts created
        
        # Assert the response content contains post titles and category
        self.assertContains(response, "Test Post 1")
        self.assertContains(response, "Test Post 2")
        self.assertContains(response, "Test Category")
        
        # Assert subscriber count is 0 (no subscribers created)
        self.assertEqual(response.context['subscriber_count'], 0)

    def test_blog_index_hx_request_empty_posts_edge_case(self):
        """
        Edge Case: Test HX-Request with no published posts.
        """
        # Delete all posts to simulate empty state
        Post.objects.all().delete()
        
        # Simulate a request with HX-Request header
        response = self.client.get(
            reverse('index'),
            HTTP_HX_REQUEST='true'
        )
        
        # Assert the correct template is used
        self.assertTemplateUsed(response, 'blog/partials/post_list.html')
        
        # Assert the response status code is 200
        self.assertEqual(response.status_code, 200)
        
        # Assert the context contains 'posts' with no items
        self.assertIn('posts', response.context)
        self.assertEqual(len(response.context['posts']), 0)
        
        self.assertContains(response, "")

class SubscribeViewTests(TestCase):
    def setUp(self):
        # Set up test client
        self.client = Client()
        
        # Mock settings.BREVO_API_KEY
        self.brevo_api_key = "test-api-key"
        settings.BREVO_API_KEY = self.brevo_api_key
        
        # Mock requests.post to avoid real API calls
        self.patcher = unittest.mock.patch('requests.post')
        self.mock_post = self.patcher.start()
        self.mock_post.return_value.status_code = 200
        
    def tearDown(self):
        # Stop the patcher
        self.patcher.stop()
    
    def test_subscribe_view_unhappy_path_invalid_email(self):
        """
        Unhappy Path: Test a POST request with an invalid email.
        """
        invalid_email = "invalid-email"
        
        # Simulate a POST request with an invalid email
        response = self.client.post(
            reverse('subscribe'),
            data={'email': invalid_email},
            content_type='application/x-www-form-urlencoded'
        )
        
        # Assert response status code and error message
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {"success": False, "error": "Invalid email address."})
        
        # Assert no API call was made
        self.mock_post.assert_not_called()
        
        # Assert no subscriber was created
        self.assertFalse(Subscriber.objects.filter(email=invalid_email).exists())

    def test_subscribe_view_edge_case_empty_email(self):
        """
        Edge Case: Test a POST request with an empty email field.
        """
        # Simulate a POST request with an empty email
        response = self.client.post(
            reverse('subscribe'),
            data={'email': ''},
            content_type='application/x-www-form-urlencoded'
        )
        
        # Assert response status code and error message
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {"success": False, "error": "Invalid email address."})
        
        # Assert no API call was made
        self.mock_post.assert_not_called()
        
        # Assert no subscriber was created
        self.assertFalse(Subscriber.objects.filter(email='').exists())

    def test_subscribe_view_edge_case_non_post_request(self):
        """
        Edge Case: Test a non-POST request (e.g., GET).
        """
        # Simulate a GET request
        response = self.client.get(reverse('subscribe'))
        
        # Assert response status code and error message
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {"success": False, "error": "Invalid request."})
        
        # Assert no API call was made
        self.mock_post.assert_not_called()