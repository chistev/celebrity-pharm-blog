from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Post, Category, Subscriber
from django.contrib.auth.models import User

class PostDetailViewTest(TestCase):
    def setUp(self):
        # Set up test client
        self.client = Client()

        # Create a category
        self.category = Category.objects.create(
            title="Test Category",
            description="A test category",
            image="category_images/test.jpg",
            slug="test-category"
        )

        # Create a published post
        self.post = Post.objects.create(
            title="Test Post",
            excerpt="This is a test excerpt.",
            image="post_images/test.jpg",
            slug="test-post",
            category=self.category,
            content="This is the content of the test post.",
            status="published",
            created_at=timezone.now()
        )

        # Create another post in the same category for related posts
        self.related_post = Post.objects.create(
            title="Related Post",
            excerpt="This is a related post excerpt.",
            image="post_images/related.jpg",
            slug="related-post",
            category=self.category,
            content="This is the content of the related post.",
            status="published",
            created_at=timezone.now()
        )

        # Create a post in a different category
        self.other_category = Category.objects.create(
            title="Other Category",
            description="Another test category",
            image="category_images/other.jpg",
            slug="other-category"
        )
        self.other_post = Post.objects.create(
            title="Other Post",
            excerpt="This is another post excerpt.",
            image="post_images/other.jpg",
            slug="other-post",
            category=self.other_category,
            content="This is the content of another post.",
            status="published",
            created_at=timezone.now()
        )

        # Create a draft post
        self.draft_post = Post.objects.create(
            title="Draft Post",
            excerpt="This is a draft post excerpt.",
            image="post_images/draft.jpg",
            slug="draft-post",
            category=self.category,
            content="This is the content of a draft post.",
            status="draft",
            created_at=timezone.now()
        )

        # Create a confirmed subscriber
        self.subscriber = Subscriber.objects.create(
            email="test@example.com",
            is_confirmed=True,
            confirmation_token="test-token",
            token_created_at=timezone.now()
        )

    def test_post_detail_view_with_published_post(self):
        """Test that a published post is displayed correctly."""
        url = reverse('post_detail', args=[self.post.slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['subscriber_count'], 1)
        self.assertIn(self.related_post, response.context['related_posts'])
        self.assertNotIn(self.other_post, response.context['related_posts'])
        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.content)

    def test_post_detail_view_with_draft_post(self):
        """Test that accessing a draft post returns 404."""
        url = reverse('post_detail', args=[self.draft_post.slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_with_nonexistent_post(self):
        """Test that accessing a nonexistent post returns 404."""
        url = reverse('post_detail', args=['nonexistent-post'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_post_detail_view_related_posts(self):
        """Test that related posts are from the same category and exclude the current post."""
        url = reverse('post_detail', args=[self.post.slug])
        response = self.client.get(url)

        related_posts = response.context['related_posts']
        self.assertNotIn(self.post, related_posts)  # Current post should not be in related posts
        self.assertNotIn(self.other_post, related_posts)  # Post from different category should not be included

    def test_post_detail_view_subscriber_count(self):
        """Test that the subscriber count is correct."""
        url = reverse('post_detail', args=[self.post.slug])
        response = self.client.get(url)

        self.assertEqual(response.context['subscriber_count'], 1)

        # Add another confirmed subscriber
        Subscriber.objects.create(
            email="another@example.com",
            is_confirmed=True,
            confirmation_token="another-token",
            token_created_at=timezone.now()
        )

        response = self.client.get(url)
        self.assertEqual(response.context['subscriber_count'], 2)

    def test_post_detail_view_template_content(self):
        """Test that the response contains expected content from the post."""
        url = reverse('post_detail', args=[self.post.slug])
        response = self.client.get(url)

        self.assertContains(response, self.post.title)
        self.assertContains(response, self.post.excerpt)
        self.assertContains(response, self.post.content)
        self.assertContains(response, self.related_post.title)

class SearchViewTest(TestCase):
    def setUp(self):
        # Set up test client
        self.client = Client()

        # Create a category
        self.category = Category.objects.create(
            title="Test Category",
            description="A test category",
            image="category_images/test.jpg",
            slug="test-category"
        )

        # Create published posts for search
        self.post1 = Post.objects.create(
            title="Python Programming",
            excerpt="Learn Python programming basics.",
            image="post_images/python.jpg",
            slug="python-programming",
            category=self.category,
            content="Content about Python programming.",
            status="published",
            created_at=timezone.now()
        )

        self.post2 = Post.objects.create(
            title="Django Tutorial",
            excerpt="A tutorial on Django programming framework.",  # Updated to include "programming"
            image="post_images/django.jpg",
            slug="django-tutorial",
            category=self.category,
            content="Content about Django framework.",
            status="published",
            created_at=timezone.now()
        )

        self.post3 = Post.objects.create(
            title="JavaScript Guide",
            excerpt="This is about JavaScript.",
            image="post_images/js.jpg",
            slug="javascript-guide",
            category=self.category,
            content="Content about JavaScript.",
            status="published",
            created_at=timezone.now()
        )

        # Create a draft post (should not appear in search)
        self.draft_post = Post.objects.create(
            title="Draft Post",
            excerpt="This is a draft post.",
            image="post_images/draft.jpg",
            slug="draft-post",
            category=self.category,
            content="Draft content.",
            status="draft",
            created_at=timezone.now()
        )

    def test_search_view_happy_path(self):
        """Test search with a valid query that matches posts."""
        url = reverse('search') + '?q=python'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/search_results.html')
        self.assertEqual(response.context['query'], 'python')
        
        posts = response.context['posts']
        self.assertIn(self.post1, posts)
        self.assertNotIn(self.post2, posts)
        self.assertNotIn(self.post3, posts)
        self.assertNotIn(self.draft_post, posts)
        
        self.assertEqual(len(posts), 1)
        self.assertContains(response, self.post1.title)
        self.assertContains(response, self.post1.excerpt)
        self.assertNotContains(response, self.post2.title)
        self.assertNotContains(response, self.draft_post.title)

    def test_search_view_multiple_results_with_pagination(self):
        """Test search with multiple results and pagination."""
        url = reverse('search') + '?q=programming'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/search_results.html')
        self.assertEqual(response.context['query'], 'programming')
        
        posts = response.context['posts']
        self.assertIn(self.post1, posts)
        self.assertIn(self.post2, posts)  # Now matches due to updated excerpt
        self.assertNotIn(self.post3, posts)
        self.assertNotIn(self.draft_post, posts)
        
        self.assertTrue(len(posts) <= 4)
        self.assertContains(response, self.post1.title)
        self.assertContains(response, self.post2.title)

        url = reverse('search') + '?q=programming&page=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        posts = response.context['posts']

    def test_search_view_unhappy_path_no_results(self):
        """Test search with a query that matches no posts."""
        url = reverse('search') + '?q=nonexistent'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/search_results.html')
        self.assertEqual(response.context['query'], 'nonexistent')
        
        posts = response.context['posts']
        self.assertEqual(len(posts), 0)
        self.assertNotContains(response, self.post1.title)
        self.assertNotContains(response, self.post2.title)
        self.assertNotContains(response, self.post3.title)
        self.assertNotContains(response, self.draft_post.title)

    def test_search_view_empty_query(self):
        """Test search with an empty query string."""
        url = reverse('search') + '?q='
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/search_results.html')
        self.assertEqual(response.context['query'], '')
        
        posts = response.context['posts']
        self.assertIn(self.post1, posts)
        self.assertIn(self.post2, posts)
        self.assertIn(self.post3, posts)
        self.assertNotIn(self.draft_post, posts)
        self.assertEqual(len(posts), 3)
        self.assertContains(response, self.post1.title)
        self.assertContains(response, self.post2.title)
        self.assertContains(response, self.post3.title)

    def test_search_view_no_query_parameter(self):
        """Test search without a query parameter."""
        url = reverse('search')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/search_results.html')
        self.assertEqual(response.context['query'], '')
        
        posts = response.context['posts']
        self.assertIn(self.post1, posts)
        self.assertIn(self.post2, posts)
        self.assertIn(self.post3, posts)
        self.assertNotIn(self.draft_post, posts)
        self.assertEqual(len(posts), 3)

    def test_search_view_case_insensitive(self):
        """Test that search is case-insensitive."""
        url = reverse('search') + '?q=PYTHON'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/search_results.html')
        self.assertEqual(response.context['query'], 'PYTHON')
        
        posts = response.context['posts']
        self.assertIn(self.post1, posts)
        self.assertNotIn(self.post2, posts)
        self.assertNotIn(self.post3, posts)
        self.assertNotIn(self.draft_post, posts)
        self.assertContains(response, self.post1.title)

    def test_search_view_special_characters(self):
        """Test search with special characters in query."""
        url = reverse('search') + '?q=python!!!'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/search_results.html')
        self.assertEqual(response.context['query'], 'python!!!')
        
        posts = response.context['posts']
        self.assertIn(self.post1, posts)
        self.assertNotIn(self.post2, posts)
        self.assertNotIn(self.post3, posts)
        self.assertNotIn(self.draft_post, posts)
        self.assertContains(response, self.post1.title)

    def test_search_view_order_by_created_at(self):
        """Test that search results are ordered by created_at descending."""
        newer_post = Post.objects.create(
            title="Newer Python Post",
            excerpt="Newer post about Python.",
            image="post_images/newer.jpg",
            slug="newer-python-post",
            category=self.category,
            content="Newer content about Python.",
            status="published",
            created_at=timezone.now() + timezone.timedelta(minutes=10)
        )

        url = reverse('search') + '?q=python'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        posts = response.context['posts']
        
        self.assertEqual(list(posts)[0], newer_post)
        self.assertEqual(list(posts)[1], self.post1)