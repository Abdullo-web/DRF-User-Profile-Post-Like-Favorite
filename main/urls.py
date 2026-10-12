from django.urls import path
from .views import *

urlpatterns = [
    path('users/',users),
    path('users/<int:id>/',users_id),
    path('users/most-active/', most_active),
    path('users/statistics/', users_statistics),
    
    path('profiles/', profiles),
    path('profiles/<int:id>/', profiles_id),
    path('profiles/city-statistics/', city_statistics),
    
    path('posts/', posts),
    path('posts/popular/', popular_posts),
    path('posts/<int:id>/', posts_id),
    
    path('users/<int:id>/posts/', user_posts),
]
