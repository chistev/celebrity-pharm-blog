import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from blog.models import Post, Category
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Populate the database with sample posts'

    def handle(self, *args, **options):
        # Delete all existing posts
        Post.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Deleted all existing posts."))

        # Fetch categories from the database
        health_category = Category.objects.get(slug='health-tips')  # Fetch Health Tips category object
        personal_life_category = Category.objects.get(slug='personal-life')  # Fetch Personal Life category object

        # Path to your static image
        image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'celeb_pharm.png')

        # Check if image exists
        if not os.path.exists(image_path):
            self.stdout.write(self.style.ERROR(f"Image not found at {image_path}"))
            return

        posts_data = [
            {'title': 'The Science of Sleep: Optimizing Your Rest', 'excerpt': 'Explore the science behind sleep and learn how to optimize your rest for better health and productivity.', 'category': health_category},
            {'title': 'Mindful Eating: A Guide to Healthier Habits', 'excerpt': 'Discover the principles of mindful eating and how it can transform your relationship with food.', 'category': health_category},
            {'title': 'My Journey Through Pharmacy School', 'excerpt': 'A personal reflection on my experiences and challenges during pharmacy school.', 'category': personal_life_category},
            {'title': 'Balancing Work and Life: My Personal Tips', 'excerpt': 'Practical advice on achieving a healthy work-life balance, based on my own experiences.', 'category': personal_life_category},
            {'title': 'Understanding Supplements: What Works and What Doesn’t', 'excerpt': 'A breakdown of popular supplements, backed by science.', 'category': health_category},
            {'title': 'Daily Routines for Better Mental Health', 'excerpt': 'Tips to incorporate into your day to improve focus, mood, and clarity.', 'category': health_category},
            {'title': 'Breaking Down Blood Pressure Myths', 'excerpt': 'Separating facts from fiction when it comes to hypertension.', 'category': health_category},
            {'title': 'Healthy Habits for Night Shift Workers', 'excerpt': 'A survival guide for health and sleep when working odd hours.', 'category': health_category},
            {'title': 'Staying Fit Without the Gym', 'excerpt': 'Creative ways to maintain your fitness from home or outdoors.', 'category': health_category},
            {'title': 'Journaling for Mental Clarity', 'excerpt': 'How writing can help manage stress and promote emotional wellness.', 'category': health_category},
            {'title': 'Reading Labels Like a Pro: Pharmacy Edition', 'excerpt': 'A guide to decoding medication and supplement labels accurately.', 'category': health_category},
            {'title': 'From Burnout to Balance: A Pharmacist’s Story', 'excerpt': 'Sharing my journey from professional burnout to recovery and balance.', 'category': personal_life_category},
            {'title': 'How to Stay Focused During Long Study Sessions', 'excerpt': 'Effective study tips to stay focused for hours at a time.', 'category': personal_life_category},
            {'title': 'The Art of Saying No: Setting Healthy Boundaries', 'excerpt': 'Learn how to say no without guilt and protect your mental health.', 'category': personal_life_category},
            {'title': 'Building Resilience: How to Bounce Back from Setbacks', 'excerpt': 'Practical steps to help you build emotional strength and resilience.', 'category': personal_life_category},
            {'title': 'The Power of Networking in Pharmacy School', 'excerpt': 'How building relationships can open doors and shape your career.', 'category': personal_life_category},
            {'title': 'How to Manage Stress During Exams', 'excerpt': 'Proven techniques to handle exam pressure and perform well.', 'category': personal_life_category},
            {'title': 'Nutrition for Busy Professionals', 'excerpt': 'Quick and easy meal ideas that support energy and productivity.', 'category': health_category},
            {'title': 'The Importance of Hydration for Mental Health', 'excerpt': 'Why drinking enough water is essential for your emotional and physical well-being.', 'category': health_category},
            {'title': 'Sleep Hygiene Tips for Better Quality Rest', 'excerpt': 'Simple steps to improve the quality of your sleep.', 'category': health_category},
            {'title': 'How to Build a Successful Morning Routine', 'excerpt': 'Start your day right with a routine that sets the tone for success.', 'category': personal_life_category},
            {'title': 'Meditation for Beginners: How to Get Started', 'excerpt': 'A guide to meditation techniques that will calm your mind and reduce anxiety.', 'category': health_category},
            {'title': 'The Role of Exercise in Mental Health', 'excerpt': 'How physical activity boosts mood and mental clarity.', 'category': health_category},
            {'title': 'A Guide to Overcoming Procrastination', 'excerpt': 'Simple strategies to break the procrastination habit and get things done.', 'category': personal_life_category},
            {'title': 'How to Achieve Your Long-Term Goals', 'excerpt': 'Tips to help you set and accomplish your most important life goals.', 'category': personal_life_category}
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
                category=post_data['category'],  # Assigning the category object here
            )

            with open(image_path, 'rb') as img_file:
                post.image.save('celeb_pharm.png', File(img_file), save=False)

            post.save()
            self.stdout.write(self.style.SUCCESS(f"Created post '{post.title}'"))

        self.stdout.write(self.style.SUCCESS("Database population complete."))
