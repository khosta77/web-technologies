"""
URL configuration for askpupkin project.
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def ask(request):
    return render(request, 'ask.html')

def login_view(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def question(request, question_id):
    return render(request, 'question.html')

def settings(request):
    return render(request, 'settings.html')

def tags(request):
    return render(request, 'tags.html')

def hot(request):
    return render(request, 'index.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('ask/', ask, name='ask'),
    path('login/', login_view, name='login'),
    path('register/', signup, name='signup'),
    path('question/<int:question_id>/', question, name='question'),
    path('settings/', settings, name='settings'),
    path('tags/', tags, name='tags'),
    path('tag/<str:tag_name>/', tags, name='tag'),
    path('hot/', hot, name='hot'),
]
