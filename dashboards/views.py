from django.shortcuts import get_object_or_404, redirect, render
from blog.models import category,Blog
from django.contrib.auth.decorators import login_required

from dashboards.forms import CategoryForm


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