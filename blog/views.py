from django.utils import timezone
from django.shortcuts import redirect
from django.conf import settings
import requests
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, JsonResponse
from django.urls import reverse

from .models import Post, Category, Subscriber, UnsubscribeToken

from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from django.db.models import Q

from django.contrib.syndication.views import Feed

from django.views import View

signer = TimestampSigner()

def blog_index(request: HttpRequest):
    post_list = Post.objects.filter(status='published').order_by('-created_at')
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

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"success": False, "error": "Invalid email address."})

        if Subscriber.objects.filter(email=email, is_confirmed=True).exists():
            return JsonResponse({"success": False, "error": "Email already subscribed."})

        token = signer.sign(email)
        confirm_url = request.build_absolute_uri(
            reverse("confirm_subscription") + f"?token={token}"
        )

        brevo_api_key = settings.BREVO_API_KEY
        requests.post(
            'https://api.brevo.com/v3/smtp/email',
            headers={
                'accept': 'application/json',
                'api-key': brevo_api_key,
                'content-type': 'application/json',
            },
            json={
                "sender": {"name": "Celebritypharm", "email": "unique@celebritypharm.com"},
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

class HandleUnsubscribeView(View):
    def get(self, request):
        token_value = request.GET.get('token')
        if not token_value:
            return redirect('unsubscribe-status', status='invalid')

        try:
            token = UnsubscribeToken.objects.get(token=token_value)
        except (UnsubscribeToken.DoesNotExist, ValidationError):
            return redirect('unsubscribe-status', status='invalid')

        if token.is_expired():
            return redirect('unsubscribe-status', status='expired')

        if token.unsubscribed:
            return redirect('unsubscribe-status', status='already')

        # Delete subscriber and mark token unsubscribed
        Subscriber.objects.filter(email=token.email).delete()
        token.unsubscribed = True
        token.save()

        return redirect('unsubscribe-status', status='success')

class UnsubscribeStatusView(View):
    def get(self, request, status):
        template_map = {
            'invalid': 'blog/invalid.html',
            'expired': 'blog/expired.html',
            'already': 'blog/already.html',
            'success': 'blog/success.html',
        }
        template_name = template_map.get(status, 'unsubscribe/invalid.html')
        return render(request, template_name)
    
def categories(request):
    categories = Category.objects.all()
    return render(request, 'blog/categories.html', {'categories': categories})

def about(request):
    return render(request, 'blog/about.html')

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')

     # Fetch related posts from the same category, excluding the current post
    related_posts = Post.objects.filter(category=post.category).exclude(id=post.id)[:3]

    subscriber_count = Subscriber.objects.filter(is_confirmed=True).count()
    
    return render(request, 'blog/post_detail.html', {'post': post, 'related_posts': related_posts,
                                                      'subscriber_count': subscriber_count })

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category)
    
    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Return the context to the template
    return render(request, 'blog/category_detail.html', {
        'category': category,
        'posts': posts,
    })

def search(request):
    query = request.GET.get('q', '')
    posts = Post.objects.filter(
        Q(title__icontains=query) | Q(excerpt__icontains=query)
    )
    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    return render(request, 'blog/search_results.html', {
        'posts': posts,
        'query': query
    })


class LatestPostsFeed(Feed):
    title = "Celebritypharm Blog - Latest Posts"
    
    # Link to the site or the RSS feed page
    link = "/rss/"
    
    description = "Stay updated with the latest posts from Celebritypharm blog."

    # Items to include in the feed (latest 10 posts)
    def items(self):
        return Post.objects.filter(status='published').order_by('-created_at')[:10]

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return item.get_absolute_url()

    def item_description(self, item):
        return item.excerpt

    def item_pubdate(self, item):
        return item.created_at
