from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Post

def blog_index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 4)

    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'posts': posts})

def categories(request):
    return render(request, 'blog/categories.html')

def about(request):
    return render(request, 'blog/about.html')

def post_detail(request):
    return render(request, 'blog/post_detail.html') 

def category_detail(request):
    return render(request, 'blog/category_detail.html')
