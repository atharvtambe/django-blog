from django.shortcuts import render,redirect
from django.http import request
from django.core.paginator import Paginator
from blog.models import category,Blog
from .forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth

def home(request):
    categories = category.objects.all()
    featured_posts = list(Blog.objects.filter(
        is_featured=True,
        status='Published',
    ).order_by('-created_at')[:4])
    post_list = Blog.objects.filter(
        status='Published',
    ).exclude(pk__in=[post.pk for post in featured_posts]).order_by('-created_at')
    posts = Paginator(post_list, 6).get_page(request.GET.get('page'))

    context = {
        'categories': categories,
        'featured_posts': featured_posts,
        'posts': posts,
        'posts_page': posts,
    }
    return render(request, 'home.html', context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('register')
        else:
            print(form.errors)
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'register.html', context)

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
            return redirect('dashboard')
    form = AuthenticationForm()
    context = {
        'form': form,
    }
    return render(request, 'login.html', context)


def logout(request):
    auth.logout(request)
    return redirect('home')