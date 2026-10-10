from django.contrib import admin
from .models import category, Blog, Comment


class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'category', 'author', 'status', 'is_ai_generated', 'generation_date', 'is_featured')
    list_filter = ('status', 'is_ai_generated', 'category', 'is_featured')
    search_fields = ('title', 'id', 'category__category_name', 'status', 'blog_body')
    readonly_fields = ('generation_date',)


admin.site.register(category)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Comment)