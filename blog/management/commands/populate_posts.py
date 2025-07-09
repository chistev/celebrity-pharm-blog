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
            {
                'title': 'The Science of Sleep: Optimizing Your Rest',
                'excerpt': 'Explore the science behind sleep and learn how to optimize your rest for better health and productivity.',
                'content': '<p>Sleep is crucial for both physical and mental well-being. In this article, we explore the science behind sleep, the benefits of good rest, and how to optimize your sleep schedule for better productivity.</p>',
                'category': health_category
            },
            {
                'title': 'Mindful Eating: A Guide to Healthier Habits',
                'excerpt': 'Discover the principles of mindful eating and how it can transform your relationship with food.',
                'content': '<p>Mindful eating is a practice that focuses on being present while eating. By tuning into your body’s hunger cues and savoring your food, you can develop a healthier relationship with food and improve digestion.</p>',
                'category': health_category
            },
            {
                'title': 'My Journey Through Pharmacy School',
                'excerpt': 'A personal reflection on my experiences and challenges during pharmacy school.',
                'content': '<p>Pharmacy school was a challenging but rewarding experience. From late-night study sessions to hands-on internships, this article shares my journey through pharmacy school and the lessons I learned along the way.</p>',
                'category': personal_life_category
            },
            {
                'title': 'Balancing Work and Life: My Personal Tips',
                'excerpt': 'Practical advice on achieving a healthy work-life balance, based on my own experiences.',
                'content': '<p>Achieving a healthy work-life balance can be tough. In this post, I share my personal tips and strategies that have helped me balance work, school, and personal time, while avoiding burnout.</p>',
                'category': personal_life_category
            },
            {
                'title': 'Understanding Supplements: What Works and What Doesn’t',
                'excerpt': 'A breakdown of popular supplements, backed by science.',
                'content': '<p>Supplements are a billion-dollar industry, but how do you know which ones actually work? This post covers the most popular supplements, what the research says about them, and how to make informed decisions.</p>',
                'category': health_category
            },
            {
                'title': 'Daily Routines for Better Mental Health',
                'excerpt': 'Tips to incorporate into your day to improve focus, mood, and clarity.',
                'content': '<p>Our daily routines have a profound impact on mental health. By integrating simple habits such as journaling, meditation, and exercise, you can improve mental clarity and emotional well-being. This article dives into the best practices for mental health management.</p>',
                'category': health_category
            },
            {
                'title': 'Breaking Down Blood Pressure Myths',
                'excerpt': 'Separating facts from fiction when it comes to hypertension.',
                'content': '<p>High blood pressure is one of the most common health conditions, but many myths still surround it. In this post, we break down common misconceptions and provide scientifically backed information on managing and preventing hypertension.</p>',
                'category': health_category
            },
            {
                'title': 'Healthy Habits for Night Shift Workers',
                'excerpt': 'A survival guide for health and sleep when working odd hours.',
                'content': '<p>Working night shifts can be tough on your health. From irregular sleep patterns to poor nutrition, night shift workers face unique challenges. This post offers practical tips for staying healthy while working odd hours, ensuring proper sleep, and managing stress.</p>',
                'category': health_category
            },
            {
                'title': 'Staying Fit Without the Gym',
                'excerpt': 'Creative ways to maintain your fitness from home or outdoors.',
                'content': '<p>You don’t need a gym membership to stay fit! This post explores fun and creative ways to stay active, from bodyweight exercises at home to outdoor activities like hiking and cycling. Get fit on your terms!</p>',
                'category': health_category
            },
            {
                'title': 'Journaling for Mental Clarity',
                'excerpt': 'How writing can help manage stress and promote emotional wellness.',
                'content': '<p>Journaling is an incredibly effective tool for managing stress and gaining mental clarity. Whether you’re reflecting on your day or exploring your emotions, writing can help you process your thoughts and improve emotional well-being. This article provides tips on how to start journaling for mental health.</p>',
                'category': health_category
            },
            {
                'title': 'Reading Labels Like a Pro: Pharmacy Edition',
                'excerpt': 'A guide to decoding medication and supplement labels accurately.',
                'content': '<p>Reading medication and supplement labels is crucial for making informed decisions. In this post, we decode common terms and symbols found on labels, so you can understand exactly what you’re putting into your body. Get empowered with knowledge!</p>',
                'category': health_category
            },
            {
                'title': 'From Burnout to Balance: A Pharmacist’s Story',
                'excerpt': 'Sharing my journey from professional burnout to recovery and balance.',
                'content': '<p>As a pharmacist, I experienced burnout early in my career. In this post, I share my personal journey of overcoming burnout and finding a healthy work-life balance. If you’re feeling overwhelmed, you’re not alone – and there’s hope for recovery.</p>',
                'category': personal_life_category
            },
            {
                'title': 'How to Stay Focused During Long Study Sessions',
                'excerpt': 'Effective study tips to stay focused for hours at a time.',
                'content': '<p>Staying focused during long study sessions can be difficult, especially when distractions abound. In this post, I share techniques that helped me stay on track during long hours of studying, including the Pomodoro Technique, breaks, and healthy study habits.</p>',
                'category': personal_life_category
            },
            {
                'title': 'The Art of Saying No: Setting Healthy Boundaries',
                'excerpt': 'Learn how to say no without guilt and protect your mental health.',
                'content': '<p>Setting boundaries is essential for mental and emotional health, but it can be difficult to say no without feeling guilty. In this post, I teach you how to assertively set boundaries, prioritize your well-being, and maintain healthy relationships without compromising your peace.</p>',
                'category': personal_life_category
            },
            {
                'title': 'Building Resilience: How to Bounce Back from Setbacks',
                'excerpt': 'Practical steps to help you build emotional strength and resilience.',
                'content': '<p>Life is full of challenges, and building resilience is key to overcoming setbacks. In this post, I share the importance of resilience, along with practical tips on how to bounce back stronger from life’s difficult moments.</p>',
                'category': personal_life_category
            },
            {
                'title': 'The Power of Networking in Pharmacy School',
                'excerpt': 'How building relationships can open doors and shape your career.',
                'content': '<p>Networking isn’t just for job seekers – it’s an essential part of your career development, especially in pharmacy school. In this article, I discuss how to build meaningful connections, seek mentorship, and leverage your network to shape your career.</p>',
                'category': personal_life_category
            },
            {
                'title': 'How to Manage Stress During Exams',
                'excerpt': 'Proven techniques to handle exam pressure and perform well.',
                'content': '<p>Exams can be stressful, but with the right techniques, you can manage that stress and perform at your best. In this post, I cover effective stress-management strategies, including time management, breathing exercises, and staying positive during exam week.</p>',
                'category': personal_life_category
            },
            {
                'title': 'Nutrition for Busy Professionals',
                'excerpt': 'Quick and easy meal ideas that support energy and productivity.',
                'content': '<p>As a busy professional, it’s easy to skip meals or rely on fast food. However, eating the right foods is crucial for maintaining energy levels and productivity. This post provides simple, nutritious meal ideas that fit into even the busiest schedules.</p>',
                'category': health_category
            },
            {
                'title': 'The Importance of Hydration for Mental Health',
                'excerpt': 'Why drinking enough water is essential for your emotional and physical well-being.',
                'content': '<p>Hydration plays a crucial role in mental health. Dehydration can cause fatigue, mood swings, and difficulty focusing. In this article, we explain the importance of staying hydrated and offer tips on how to maintain optimal hydration throughout the day.</p>',
                'category': health_category
            },
            {
                'title': 'Sleep Hygiene Tips for Better Quality Rest',
                'excerpt': 'Simple steps to improve the quality of your sleep.',
                'content': '<p>Good sleep hygiene is essential for getting restful sleep. In this post, we cover the habits and environmental factors that contribute to better sleep quality, including creating a sleep-friendly environment and following a consistent sleep schedule.</p>',
                'category': health_category
            },
            {
                'title': 'How to Build a Successful Morning Routine',
                'excerpt': 'Start your day right with a routine that sets the tone for success.',
                'content': '<p>Your morning routine sets the tone for the rest of your day. In this article, I share the key habits to include in your morning routine to increase productivity, improve mental clarity, and set yourself up for success each day.</p>',
                'category': personal_life_category
            },
            {
                'title': 'Meditation for Beginners: How to Get Started',
                'excerpt': 'A guide to meditation techniques that will calm your mind and reduce anxiety.',
                'content': '<p>Meditation is a powerful tool for reducing stress and improving mental clarity. In this post, I guide you through the basics of meditation, offering simple techniques to get started, even if you’ve never meditated before.</p>',
                'category': health_category
            },
            {
                'title': 'The Role of Exercise in Mental Health',
                'excerpt': 'How physical activity boosts mood and mental clarity.',
                'content': '<p>Exercise isn’t just good for your body – it’s also great for your mind. In this post, I explain how physical activity can improve mental health, boost your mood, and enhance mental clarity, along with the best types of exercises for mental well-being.</p>',
                'category': health_category
            },
            {
                'title': 'A Guide to Overcoming Procrastination',
                'excerpt': 'Simple strategies to break the procrastination habit and get things done.',
                'content': '<p>Procrastination can be a major roadblock to achieving your goals. In this post, we explore effective strategies to overcome procrastination, including time management, goal setting, and using rewards as motivation.</p>',
                'category': personal_life_category
            },
            {
                'title': 'How to Achieve Your Long-Term Goals',
                'excerpt': 'Tips to help you set and accomplish your most important life goals.',
                'content': '<p>Setting long-term goals can be daunting, but with a clear plan, they are entirely achievable. In this post, I provide a step-by-step guide to help you set, pursue, and achieve your most important long-term goals, while staying motivated along the way.</p>',
                'category': personal_life_category
            }
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
                content=post_data['content'],  # Adding content here
            )

            # Add image for the post
            with open(image_path, 'rb') as img_file:
                post.image.save('celeb_pharm.png', File(img_file), save=False)

            # Save post
            post.save()
            self.stdout.write(self.style.SUCCESS(f"Created post '{post.title}'"))

        self.stdout.write(self.style.SUCCESS("Database population complete."))
