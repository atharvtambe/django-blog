"""
URL configuration for blog_main project.
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from . import views
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
]

# Serve uploaded media files during local development only.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
