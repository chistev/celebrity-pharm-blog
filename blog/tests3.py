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