from django.test import TestCase, Client
from django.urls import reverse
from blog.models import Category, Post, Subscriber

class BlogIndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('index')

    def test_blog_index_returns_only_published_posts_in_order(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.context)

        posts = response.context['posts'].object_list  # Paginated queryset

        for post in posts:
            self.assertEqual(post.status, 'published', f"Post {post.title} is not published")

        created_dates = [post.created_at for post in posts]
        self.assertEqual(created_dates, sorted(created_dates, reverse=True), "Posts are not ordered by most recent")

    def test_blog_index_pagination_limit(self):
        """
        Test that the blog index view paginates to 4 posts per page.
        Uses existing posts in the database.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('posts', response.context)

        posts_page = response.context['posts']
        self.assertEqual(posts_page.paginator.per_page, 4, "Pagination is not limited to 4 posts per page")
        self.assertLessEqual(len(posts_page.object_list), 4, "More than 4 posts returned on one page")

    def test_blog_index_includes_subscriber_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('subscriber_count', response.context)

        # Confirm subscriber_count matches the count in the DB (could be zero)
        confirmed_count = Subscriber.objects.filter(is_confirmed=True).count()
        self.assertEqual(response.context['subscriber_count'], confirmed_count)

    def test_blog_index_includes_categories(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('categories', response.context)

        categories = response.context['categories']
        all_categories = Category.objects.all()
        self.assertQuerySetEqual(
            categories.order_by('pk'),
            all_categories.order_by('pk'),
            transform=lambda x: x
        )

    def test_blog_index_hx_request_renders_partial(self):
        response = self.client.get(self.url, HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        
        self.assertTemplateUsed(response, 'blog/partials/post_list.html')
        
        # Ensure 'posts' is in the context and is a page object (paginated)
        self.assertIn('posts', response.context)
        posts = response.context['posts']
        self.assertTrue(hasattr(posts, 'object_list'), "'posts' context does not look paginated")
