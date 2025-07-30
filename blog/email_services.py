import os
import requests
from .models import Subscriber, UnsubscribeToken

def send_post_notification(post_title, post_excerpt, post_slug):
    api_key = os.environ.get('BREVO_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the 'BREVO_API_KEY' environment variable.")

    api_url = 'https://api.brevo.com/v3/smtp/email'
    sender_email = 'unique@celebritypharm.com'
    sender_name = 'CelebrityPharm'
    reply_to_email = 'celebritypharm@gmail.com'
    brevo_template_id = 12

    subscribers = Subscriber.objects.filter(is_confirmed=True)
    for subscriber in subscribers:
        token = UnsubscribeToken.objects.create(email=subscriber.email)
        unsubscribe_link = f"https://yourdomain.com/unsubscribe?token={token.token}"

        payload = {
            "sender": {
                "name": sender_name,
                "email": sender_email,
            },
            "replyTo": {
                "email": reply_to_email
            },
            "to": [
                {
                    "email": subscriber.email
                }
            ],
            "templateId": brevo_template_id,
            "params": {
                "title": post_title,
                "excerpt": post_excerpt,
                "slug": post_slug,
                "unsubscribe_link": unsubscribe_link
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api-key': api_key
        }

        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code == 201:
            print(f"✅ Email sent to {subscriber.email}")
        else:
            print(f"❌ Failed for {subscriber.email}: {response.text}")
