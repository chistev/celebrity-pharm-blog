from django.shortcuts import render, get_object_or_404

def blog_index(request):
    return render(request, 'blog/index.html')

def categories(request):
    return render(request, 'blog/categories.html')