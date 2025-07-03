from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=200)
    excerpt = models.TextField()
    image = models.ImageField(upload_to='post_images/')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='category_images/')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title
