from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('tags/', views.tags, name='tags'),
    path('login/', views.login_view, name='login'),
    path('register/', views.signup, name='signup'),
    path('ask/', views.ask, name='ask'),
    path('settings/', views.settings, name='settings'),
]

