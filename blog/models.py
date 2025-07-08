from django.db import models
from django.utils import timezone

class Post(models.Model):
    title = models.CharField(max_length=200)
    excerpt = models.TextField()
    image = models.ImageField(upload_to='post_images/')
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(
        'Category', 
        related_name='posts',  # This is the reverse relation, to get all posts in a category
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.title

class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='category_images/')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_confirmed = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=64, unique=True)
    token_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email
