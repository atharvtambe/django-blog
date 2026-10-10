"""
URL configuration for blog_main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from blog import views as Blogview

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('category/', include('blog.urls')),
    path('ai/chat/', Blogview.ai_chat, name='ai_chat'),
    path('blog/search/', Blogview.search, name='search'),
    path('blog/<int:pk>/summarize/', Blogview.summarize_blog, name='summarize_blog'),
    path('blog/<slug:slug>/', Blogview.blog, name='blog_slash'),
    path('blog/<slug:slug>', Blogview.blog, name='blog'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboards/', include('dashboards.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
