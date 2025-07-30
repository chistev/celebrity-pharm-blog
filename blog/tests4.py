from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Post, Category
from .views import LatestPostsFeed

class LatestPostsFeedTest(TestCase):
    def setUp(self):
        """Set up test data: create a category and 12 posts (10 published, 2 drafts)."""
        self.client = Client()
        self.category = Category.objects.create(
            title="Test Category",
            description="Test Description",
            slug="test-category",
            image="category_images/test.jpg"
        )

        # Create 10 published posts
        self.published_posts = []
        for i in range(10):
            post = Post.objects.create(
                title=f"Published Post {i}",
                excerpt=f"Excerpt for post {i}"[:300],
                slug=f"published-post-{i}",
                category=self.category,
                content="Test content",
                status="published",
                created_at=timezone.now(),
                image="post_images/test.jpg"
            )
            self.published_posts.append(post)

        # Create 2 draft posts
        for i in range(2):
            Post.objects.create(
                title=f"Draft Post {i}",
                excerpt=f"Excerpt for draft {i}"[:300],
                slug=f"draft-post-{i}",
                category=self.category,
                content="Test content",
                status="draft",
                created_at=timezone.now(),
                image="post_images/test.jpg"
            )

    def test_feed_metadata(self):
        """Test the feed's title, link, and description."""
        feed = LatestPostsFeed()
        self.assertEqual(feed.title, "Celebritypharm Blog - Latest Posts")
        self.assertEqual(feed.link, "/rss/")
        self.assertEqual(feed.description, "Stay updated with the latest posts from Celebritypharm blog.")

    def test_feed_items(self):
        """Test that the feed returns the 10 most recent published posts."""
        feed = LatestPostsFeed()
        items = feed.items()
        self.assertEqual(len(items), 10)
        self.assertQuerySetEqual(
            items,
            Post.objects.filter(status="published").order_by("-created_at")[:10],
            transform=lambda x: x
        )

    def test_feed_excludes_draft_posts(self):
        """Test that draft posts are not included in the feed."""
        feed = LatestPostsFeed()
        items = feed.items()
        for item in items:
            self.assertEqual(item.status, "published")

    def test_item_title(self):
        """Test that item_title returns the post's title."""
        feed = LatestPostsFeed()
        post = self.published_posts[0]
        self.assertEqual(feed.item_title(post), post.title)

    def test_item_link(self):
        """Test that item_link returns the post's absolute URL."""
        feed = LatestPostsFeed()
        post = self.published_posts[0]
        expected_url = reverse("post_detail", args=[post.slug])
        self.assertEqual(feed.item_link(post), expected_url)

    def test_item_description(self):
        """Test that item_description returns the post's excerpt."""
        feed = LatestPostsFeed()
        post = self.published_posts[0]
        self.assertEqual(feed.item_description(post), post.excerpt)

    def test_item_pubdate(self):
        """Test that item_pubdate returns the post's created_at date."""
        feed = LatestPostsFeed()
        post = self.published_posts[0]
        self.assertEqual(feed.item_pubdate(post), post.created_at)

    def test_feed_response(self):
        """Test that the RSS feed URL returns a valid response."""
        response = self.client.get(reverse("rss_feed"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/rss+xml; charset=utf-8")

    def test_feed_content(self):
        """Test that the RSS feed contains expected content."""
        response = self.client.get(reverse("rss_feed"))
        content = response.content.decode("utf-8")
        self.assertIn("<title>Celebritypharm Blog - Latest Posts</title>", content)
        self.assertIn("<link>http://testserver/rss/</link>", content)
        self.assertIn(
            "<description>Stay updated with the latest posts from Celebritypharm blog.</description>",
            content
        )
        first_post = self.published_posts[0]
        full_url = f"http://testserver{first_post.get_absolute_url()}"  # <-- FIX
        self.assertIn(f"<title>{first_post.title}</title>", content)
        self.assertIn(f"<description>{first_post.excerpt}</description>", content)
        self.assertIn(f"<link>{full_url}</link>", content)
        
    def test_feed_item_order(self):
        """Test that posts are ordered by created_at descending."""
        feed = LatestPostsFeed()
        items = feed.items()
        self.assertEqual(
            list(items.values_list("created_at", flat=True)),
            sorted(items.values_list("created_at", flat=True), reverse=True)
        )