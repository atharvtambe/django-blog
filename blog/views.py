from django.shortcuts import render

from .models import Blog,category

def post_by_category(request, category_id):
    posts = Blog.objects.filter(status='Published', category=category_id)
    
    context = {
        'posts': posts,
        'category': category,
    }
    return render(request, 'post_by_category.html', context)