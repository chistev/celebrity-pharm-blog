from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post, Category
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
        
        # Assert the response content indicates no posts (if your template handles this)
        # Adjust this based on your template's empty state rendering
        self.assertContains(response, "")  # Modify based on actual template content