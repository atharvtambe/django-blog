

from django.contrib import admin
from .models import category,Blog,Comment

class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('title',)}
    list_display = ('title','category','author','status','is_featured')
    search_fields = ('title','id','category__category_name','status')

admin.site.register(category)
admin.site.register(Blog,BlogAdmin)
admin.site.register(Comment)