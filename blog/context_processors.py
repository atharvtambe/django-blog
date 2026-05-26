from .models import category

def get_categories(request):
    categories = category.objects.all()
    return dict(categories=categories)