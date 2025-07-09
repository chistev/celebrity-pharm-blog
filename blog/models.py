from django.db import models
from django.urls import reverse
from django.utils import timezone

from django_ckeditor_5.fields import CKEditor5Field

import uuid
from datetime import timedelta

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
    content = CKEditor5Field('Content', config_name='extends')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post_detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Import here to avoid circular import issues
            from .email_services import send_post_notification
            
            post_excerpt = self.excerpt  
            send_post_notification(self.title, post_excerpt, self.slug)
    

class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='category_images/')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Categories"

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_confirmed = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=64, unique=True)
    token_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email


class UnsubscribeToken(models.Model):
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    unsubscribed = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=24)

    def __str__(self):
        return f"{self.email} - {self.token}"
    
    class Meta:
        verbose_name_plural = "Unsubscribed Users"
