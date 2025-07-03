import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from blog.models import Post
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Populate the database with sample posts'

    def handle(self, *args, **options):
        # Path to your static image
        image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'celeb_pharm.png')

        # Check if image exists
        if not os.path.exists(image_path):
            self.stdout.write(self.style.ERROR(f"Image not found at {image_path}"))
            return

        posts_data = [
            {
                'title': 'The Science of Sleep: Optimizing Your Rest',
                'excerpt': 'Explore the science behind sleep and learn how to optimize your rest for better health and productivity.',
            },
            {
                'title': 'Mindful Eating: A Guide to Healthier Habits',
                'excerpt': 'Discover the principles of mindful eating and how it can transform your relationship with food.',
            },
            {
                'title': 'My Journey Through Pharmacy School',
                'excerpt': 'A personal reflection on my experiences and challenges during pharmacy school.',
            },
            {
                'title': 'Balancing Work and Life: My Personal Tips',
                'excerpt': 'Practical advice on achieving a healthy work-life balance, based on my own experiences.',
            },
            {
                'title': 'Understanding Supplements: What Works and What Doesn’t',
                'excerpt': 'A breakdown of popular supplements, backed by science.',
            },
            {
                'title': 'Daily Routines for Better Mental Health',
                'excerpt': 'Tips to incorporate into your day to improve focus, mood, and clarity.',
            },
            {
                'title': 'Breaking Down Blood Pressure Myths',
                'excerpt': 'Separating facts from fiction when it comes to hypertension.',
            },
            {
                'title': 'Healthy Habits for Night Shift Workers',
                'excerpt': 'A survival guide for health and sleep when working odd hours.',
            },
            {
                'title': 'Staying Fit Without the Gym',
                'excerpt': 'Creative ways to maintain your fitness from home or outdoors.',
            },
            {
                'title': 'Journaling for Mental Clarity',
                'excerpt': 'How writing can help manage stress and promote emotional wellness.',
            },
            {
                'title': 'Reading Labels Like a Pro: Pharmacy Edition',
                'excerpt': 'A guide to decoding medication and supplement labels accurately.',
            },
            {
                'title': 'From Burnout to Balance: A Pharmacist’s Story',
                'excerpt': 'Sharing my journey from professional burnout to recovery and balance.',
            },
        ]

        for post_data in posts_data:
            slug = slugify(post_data['title'])
            if Post.objects.filter(slug=slug).exists():
                self.stdout.write(f"Post '{post_data['title']}' already exists. Skipping.")
                continue

            post = Post(
                title=post_data['title'],
                excerpt=post_data['excerpt'],
                slug=slug,
            )

            with open(image_path, 'rb') as img_file:
                post.image.save('celeb_pharm.png', File(img_file), save=False)

            post.save()
            self.stdout.write(self.style.SUCCESS(f"Created post '{post.title}'"))

        self.stdout.write(self.style.SUCCESS("Database population complete."))
