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
    path('posts/search/', search_posts),
    path('posts/filter/', filter_posts),
    path('posts/statistics/', posts_statistics),
    path('posts/author-statistics/', author_statistics),
    
    path('users/<int:id>/posts/', user_posts),
    

    path('likes/', likes),
    path('likes/<int:id>/', like_delete),
    
    path('posts/<int:id>/likes/', post_likes),
    
    path('likes/top-posts/', top_posts_likes),
    
    path('favorites/', favorites),
    path('favorites/<int:id>/', favorite_delete),
    
    path('users/<int:id>/favorites/', user_favorites),
    path('users/<int:id>/analytics/', user_analytics),
    
    path('dashboard/', dashboard),
]
