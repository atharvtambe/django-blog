from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from blog.models import category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = category
        fields = '__all__'
