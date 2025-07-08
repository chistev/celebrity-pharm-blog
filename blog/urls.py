from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_index, name='index'),
    path('categories/', views.categories, name='categories'),
    path('about/', views.about, name='about'),
    path('post/', views.post_detail, name='post_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path("subscribe/", views.subscribe_view, name="subscribe"),
    path("confirm-subscription/", views.confirm_subscription, name="confirm_subscription"),
     path("subscription-success/", views.subscription_success, name="subscription_success"),
]
