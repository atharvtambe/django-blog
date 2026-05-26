from django.shortcuts import render
from django.http import request
from blog.models import category,Blog

def home(request):
    categories = category.objects.all()
    featured_posts = Blog.objects.filter(is_featured=True)
    
    posts = Blog.objects.filter(is_featured=False,status='Published')


    context = {
        'categories' : categories,
        'featured_posts' : featured_posts,
        'posts' : posts,
    }
    return  render(request ,'home.html',context)