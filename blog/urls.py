from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_index, name='index'),
    path('categories/', views.categories, name='categories'),
    path('about/', views.about, name='about'),
    path('post/', views.post_detail, name='post_detail'),
    path('category/', views.category_detail, name='category_detail'),
]
