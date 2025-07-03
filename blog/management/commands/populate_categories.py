import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from blog.models import Category
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Populate the database with sample categories'

    def handle(self, *args, **options):
        categories_data = [
            {
                'title': 'Health Tips',
                'description': 'Practical advice and insights on health and wellness.',
                'image_filename': 'health_tips.avif',
            },
            {
                'title': 'Personal Life',
                'description': 'A glimpse into my life, experiences, and reflections.',
                'image_filename': 'personal_life.avif',
            },
        ]

        for cat_data in categories_data:
            slug = slugify(cat_data['title'])

            if Category.objects.filter(slug=slug).exists():
                self.stdout.write(f"Category '{cat_data['title']}' already exists. Skipping.")
                continue

            image_path = os.path.join(settings.BASE_DIR, 'static', 'images', cat_data['image_filename'])

            if not os.path.exists(image_path):
                self.stdout.write(self.style.ERROR(f"Image not found: {image_path}"))
                continue

            category = Category(
                title=cat_data['title'],
                description=cat_data['description'],
                slug=slug,
            )

            with open(image_path, 'rb') as img_file:
                category.image.save(cat_data['image_filename'], File(img_file), save=False)

            category.save()
            self.stdout.write(self.style.SUCCESS(f"Created category '{category.title}'"))

        self.stdout.write(self.style.SUCCESS("Category population complete."))
