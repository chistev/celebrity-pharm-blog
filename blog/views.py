from django.shortcuts import render

def blog_index(request):
    return render(request, 'blog/index.html')

def categories(request):
    return render(request, 'blog/categories.html')

def about(request):
    return render(request, 'blog/about.html')
