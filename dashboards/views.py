from django.shortcuts import get_object_or_404, redirect, render
from blog.models import category,Blog
from django.contrib.auth.decorators import login_required

from dashboards.forms import BlogPostForm, CategoryForm
from django.template.defaultfilters import slugify


@login_required(login_url='login')
def dashboards(request):
    category_count = category.objects.all().count()
    blogs_count = Blog.objects.all().count()

    context = {
        'category_count' : category_count,
        'blogs_count' : blogs_count
    }
    return render(request,'dashboards/dashboards.html',context)

def categories(request):
    return render(request,'dashboards/categories.html')

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    form = CategoryForm()
    context = {
        'form' : form
    }
    return render(request,'dashboards/add_category.html',context)

def delete_category(request,pk):
    Category = get_object_or_404(category, pk=pk)
    Category.delete()
    return redirect('categories')


def posts(request):
    posts = Blog.objects.all()
    context = {
        'posts': posts,
    }
    return render(request, 'dashboards/posts.html', context)

def add_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False) # temporarily saving the form
            post.author = request.user
            post.save()
            title = form.cleaned_data['title']
            post.slug = slugify(title) + '-'+str(post.id)
            post.save()
            return redirect('posts')
        else:
            print('form is invalid')
            print(form.errors)
    form = BlogPostForm()
    context = {
        'form': form,
    }
    return render(request, 'dashboards/add_post.html', context)

def edit_post(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            title = form.cleaned_data['title']
            post.slug = slugify(title) + '-'+str(post.id)
            post.save()
            return redirect('posts')
    form = BlogPostForm(instance=post)
    context = {
        'form': form,
        'post': post
    }
    return render(request, 'dashboards/edit_post.html', context)

def delete_post(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    post.delete()
    return redirect('posts')