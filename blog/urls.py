from django.urls import path
from . import views

urlpatterns = [
    path('<int:category_id>', views.post_by_category, name='post_by_category'),
    path('<int:pk>/summarize/', views.summarize_blog, name='summarize_blog_app'),
]