from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_index, name='index'),
    path('categories/', views.categories, name='categories'),
    path('about/', views.about, name='about'),
]
