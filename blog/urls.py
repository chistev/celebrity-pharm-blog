from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_index, name='index'),
    path('categories/', views.categories, name='categories'),
    path('about/', views.about, name='about'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path("subscribe/", views.subscribe_view, name="subscribe"),
    path('unsubscribe/', views.HandleUnsubscribeView.as_view(), name='handle-unsubscribe'),
    path('unsubscribe/<str:status>/', views.UnsubscribeStatusView.as_view(), name='unsubscribe-status'),
    path("confirm-subscription/", views.confirm_subscription, name="confirm_subscription"),
    path("subscription-success/", views.subscription_success, name="subscription_success"),
    path("search/", views.search, name="search"),
    path('rss/', views.LatestPostsFeed(), name='rss_feed'),
]
