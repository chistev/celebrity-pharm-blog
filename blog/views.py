from django.utils import timezone
from django.shortcuts import redirect
from django.conf import settings
import requests
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, JsonResponse
from django.urls import reverse

from .models import Post, Category, Subscriber

from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

signer = TimestampSigner()

def blog_index(request: HttpRequest):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 4)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    categories = Category.objects.all()

    subscriber_count = Subscriber.objects.filter(is_confirmed=True).count()

    if request.headers.get('HX-Request'):
        return render(request, 'blog/partials/post_list.html', {'posts': posts})
    else:
        return render(request, 'blog/index.html', {
            'posts': posts,
            'categories': categories,
            'subscriber_count': subscriber_count  
        })


def subscribe_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        # Validate format
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"success": False, "error": "Invalid email address."})

        # Check if already subscribed
        if Subscriber.objects.filter(email=email, is_confirmed=True).exists():
            return JsonResponse({"success": False, "error": "Email already subscribed."})

        # Generate signed token
        token = signer.sign(email)
        confirm_url = request.build_absolute_uri(
            reverse("confirm_subscription") + f"?token={token}"
        )

        # Send confirmation email via Brevo
        brevo_api_key = settings.BREVO_API_KEY
        requests.post(
            'https://api.brevo.com/v3/smtp/email',
            headers={
                'accept': 'application/json',
                'api-key': brevo_api_key,
                'content-type': 'application/json',
            },
            json={
                "sender": {"name": "Celebritypharm", "email": "stephen@rxjourney.net"},
                "to": [{"email": email}],
                "subject": "Confirm your subscription",
                "htmlContent": f"""
                    <p>Hi there,</p>
                    <p>Please confirm your subscription by clicking the link below:</p>
                    <p><a href="{confirm_url}">Confirm Subscription</a></p>
                    <p>This link will expire in 1 hour.</p>
                """
            }
        )

        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request."})    

def confirm_subscription(request):
    token = request.GET.get("token")

    if not token:
        return render(request, "blog/subscription_invalid.html", status=400)

    try:
        email = signer.unsign(token, max_age=3600)  # 1 hour
        subscriber, created = Subscriber.objects.get_or_create(email=email)
        subscriber.is_confirmed = True
        subscriber.confirmation_token = token
        subscriber.token_created_at = timezone.now()
        subscriber.save()
        return redirect('subscription_success')
    except SignatureExpired:
         return render(request, "blog/subscription_expired.html", status=400)
    except BadSignature:
        return render(request, "blog/subscription_invalid.html", status=400)

def subscription_success(request):
    return render(request, 'blog/subscription_success.html')

def categories(request):
    categories = Category.objects.all()
    return render(request, 'blog/categories.html', {'categories': categories})

def about(request):
    return render(request, 'blog/about.html')

def post_detail(request):
    return render(request, 'blog/post_detail.html') 

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return render(request, 'blog/category_detail.html', {'category': category})