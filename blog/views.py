from django.shortcuts import render

def blog_index(request):
    return render(request, 'blog/index.html')

def categories(request):
    return render(request, 'blog/categories.html')

def about(request):
    return render(request, 'blog/about.html')

def post_detail(request):
    return render(request, 'blog/post_detail.html') 

def category_detail(request):
    return render(request, 'blog/category_detail.html')
