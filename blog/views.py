from django.shortcuts import get_object_or_404, redirect, render

from .models import Blog,category
from django.db.models import Q


def post_by_category(request, category_id):
    posts = Blog.objects.filter(status='Published', category=category_id)
    
    context = {
        'posts': posts,
        'category': category,
    }
    return render(request, 'post_by_category.html', context)

def blog(request,slug):
    single_blog = get_object_or_404(Blog, slug=slug, status='Published')
    context = {
        'single_blog' : single_blog,
    }
    return render(request , 'blog.html',context)

def search(request):
    keyword = request.GET.get('keyword')
    
    blog = Blog.objects.filter(Q(title__icontains=keyword) | Q(short_description__icontains=keyword) | Q(blog_body__icontains=keyword), status='Published')
  


    context = {
        'blog': blog,
        'keyword': keyword,
    }
    return render(request,'search.html',context)