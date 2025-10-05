from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from django.core.exceptions import ValidationError

import uuid
from datetime import timedelta


class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='category_images/')
    slug = models.SlugField(unique=True, editable=False, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        # Auto-generate slug if not set
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200)
    excerpt = models.TextField(help_text="Max 300 characters.")
    image = models.ImageField(upload_to='post_images/')
    slug = models.SlugField(max_length=100, unique=True, editable=False, blank=True)
    category = models.ForeignKey(
        'Category',
        related_name='posts',
        on_delete=models.CASCADE,
    )
    content = CKEditor5Field('Content', config_name='extends')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=[self.slug])

    def clean(self):
        super().clean()
        if len(self.excerpt) > 300:
            raise ValidationError({'excerpt': 'Excerpt cannot be longer than 300 characters.'})

    def save(self, *args, **kwargs):
        # Auto-generate slug only once
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        self.full_clean()
        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Send notification only when a new post is published
        if is_new and self.status == 'published':
            from .email_services import send_post_notification
            send_post_notification(self.title, self.excerpt, self.slug)


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
