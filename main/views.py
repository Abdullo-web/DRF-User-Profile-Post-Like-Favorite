from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from django.db.models import Count, Avg, Min, Max, Sum, Case, When, Value, BooleanField
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta


@extend_schema(
    methods=['GET'],
    responses={200: UserSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    request=UserSerializer,
    responses={201: UserSerializer}
)
@api_view(['GET','POST'])
def users(request):
    if request.method == 'GET':
        user = User.objects.annotate(
            posts_count = Count('post',distinct=True),
            likes_count = Count('like',distinct=True),
            favorites_count = Count('favorite',distinct=True),
        )
        
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data,status=200)
    
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=201)
        return Response(serializer.errors,status=400)
         

@extend_schema(
    request=UserSerializer,
    responses={
        200: UserDetailSerializer,
        204: None,
        404: dict
    }
)

@extend_schema(
    request=UserSerializer,
    responses={
        200: UserDetailSerializer,
        204: None,
        404: dict
    }
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def users_id(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    if request.method == 'GET':
        serializer = UserDetailSerializer(user)
        return Response(serializer.data, status=200)

    if request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    if request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        user.delete()
        return Response(status=204)

# @api_view(['GET','PUT','PATCH','DELETE'])
# def users_id(request,id):
#     if request.method == 'GET':
#         user = User.objects.get(id=id)
#         serializer = UserDetailSerializer(user)
#         return Response(serializer.data)
#     if request.method == 'PUT':
#         user = User.objects.get(id=id)
#         serializer = UserSerializer(user, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=200)
#         return Response(serializer.errors, status=400)
#     if request.method == 'PATCH':
#         user = User.objects.get(id=id)
#         serializer = UserSerializer(user, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=200)
#         return Response(serializer.errors, status=400)
#     if request.method == 'DELETE':
#         user = User.objects.get(id=id)
#         user.delete()
#         return Response(status=204)
    

@api_view(['GET'])
def most_active(request):
    user = User.objects.annotate(posts_count=Count('post')).order_by('-posts_count')[:10]
    
    serializer = UserSerializer(user, many=True)
    return Response(serializer.data,status=200)


@api_view(['GET'])
def users_statistics(request):
    user = User.objects.aggregate(
        total_users = Count('id'),
        average_age = Avg('age'),
        min_age = Min('age'),
        max_age = Max('age')
        )
    
    return Response(user, status=200)


@extend_schema(
    methods=['GET'],
    responses={200: ProfileSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    request=ProfileSerializer,
    responses={201: ProfileSerializer}
)
@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
def profiles(request):
    if request.method == 'GET':
        profile = Profile.objects.annotate(
            posts_count = Count('user__post',distinct=True),
        )
        serializer = ProfileSerializer(profile, many=True)
        return Response(serializer.data, status=200)

    if request.method == 'POST':
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

@extend_schema(
    request=ProfileSerializer,
    responses={
        200: ProfileSerializer,
        204: None,
        404: dict
    }
)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def profiles_id(request, id):
    try:
        profile = Profile.objects.get(id=id)
    except Profile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=404)

    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=200)

    if request.method == 'PUT':
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    if request.method == 'PATCH':
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        profile.delete()
        return Response(status=204)

# @extend_schema(
#     request=ProfileSerializer,
#     responses={
#         200: ProfileSerializer,
#         204: None
#     }
# )
# @api_view(['GET','PUT','PATCH','DELETE'])
# def profiles_id(request,id):
#     if request.method == 'GET':
#         profile = Profile.objects.get(id=id)
#         serializer = ProfileSerializer(profile)
#         return Response(serializer.data,status=200)
    
#     if request.method == 'PUT':
#         profile = Profile.objects.get(id=id)
#         serializer = ProfileSerializer(profile, data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=200)
#         return Response(serializer.errors,status=400)
    
#     if request.method == 'PATCH':
#         profile = Profile.objects.get(id=id)
#         serializer = ProfileSerializer(profile, data= request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=200)
#         return Response(serializer.errors,status=400)
    
#     if request.method == 'DELETE':
#         profile = Profile.objects.get(id=id)
#         profile.delete()
#         return Response(status=204)
    
    

@extend_schema(
    responses={200: None}
)
@api_view(['GET'])
def city_statistics(request):
    profile = Profile.objects.values('city').annotate(
        users_count=Count('id')
    ).order_by('-users_count')

    return Response(profile, status=200)

@extend_schema(
    methods=['GET'],
    responses={200: PostSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    request=PostSerializer,
    responses={201: PostSerializer}
)
@api_view(['GET','POST'])
def posts(request):
    if request.method == 'GET':
        post = Post.objects.annotate(
            likes_count=Count('like', distinct=True),
            favorites_count=Count('favorite', distinct=True)
        ).annotate(
            is_popular=Case(
                When(likes_count__gte=10, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).order_by('-created_at')

        serializer = PostSerializer(post, many=True)
        return Response(serializer.data, status=200)
    
    if request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)



@extend_schema(
    methods=['GET'],
    responses={200: PostDetailSerializer}
)
@extend_schema(
    methods=['PUT', 'PATCH'],
    request=PostSerializer,
    responses={200: PostSerializer}
)
@extend_schema(
    methods=['DELETE'],
    responses={204: None}
)
@api_view(['GET','PUT', 'PATCH', 'DELETE'])
def posts_id(request, id):
    try:
        post = Post.objects.annotate(
            likes_count=Count('like', distinct=True),
            favorites_count=Count('favorite', distinct=True)
        ).get(id=id)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)

    if request.method == 'GET':
        serializer = PostDetailSerializer(post)
        return Response(serializer.data, status=200)
    
    if request.method == 'PUT':
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
    if request.method == 'PATCH':
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    
    if request.method == 'DELETE':
        post.delete()
        return Response(status=204)
    
    
@extend_schema(
    responses={200: serializers.Serializer}
)
@api_view(['GET'])
def user_posts(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    post = Post.objects.filter(user=user).annotate(
        likes_count=Count('like', distinct=True)
    )

    return Response({
        'user': UserPostsSerializer(user).data,
        'posts_count': post.count(),
        'results': UserPostItemSerializer(post, many=True).data
    }, status=200)
    
    
@extend_schema(
    responses={200: PopularPostSerializer(many=True)}
)

@api_view(['GET'])
def popular_posts(request):
    post = Post.objects.annotate(
        likes_count=Count('like', distinct=True),
        favorites_count=Count('favorite', distinct=True)
    ).annotate(
        is_popular=Case(
            When(likes_count__gte=10, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    ).filter(
        likes_count__gte=10
    ).order_by('-likes_count')
    
    serializer = PopularPostSerializer(post, many=True)
    return Response(serializer.data, status=200)


@extend_schema(
    responses={200: PostSearchSerializer(many=True)}
)
@api_view(['GET'])
def search_posts(request):
    q = request.query_params.get('q', '')

    post = Post.objects.filter(
        Q(title__icontains=q) | Q(content__icontains=q)
    ).annotate(
        likes_count=Count('like', distinct=True),
        favorites_count=Count('favorite', distinct=True)
    )

    serializer = PostSearchSerializer(post, many=True)
    return Response(serializer.data, status=200)


@extend_schema(
    responses={200: PostSearchSerializer(many=True)}
)
@api_view(['GET'])
def filter_posts(request):
    post = Post.objects.all()

    min_views = request.query_params.get('min_views')
    max_views = request.query_params.get('max_views')
    user_id = request.query_params.get('user_id')

    if min_views:
        post = post.filter(views__gte=min_views)

    if max_views:
        post = post.filter(views__lte=max_views)

    if user_id:
        post = post.filter(user_id=user_id)

    post = post.annotate(
        likes_count=Count('like', distinct=True),
        favorites_count=Count('favorite', distinct=True)
    )

    serializer = PostSearchSerializer(post, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
def posts_statistics(request):
    post = Post.objects.aggregate(
        total_posts=Count('id'),
        total_views=Sum('views'),
        average_views=Avg('views'),
        max_views=Max('views'),
        min_views=Min('views')
    )

    post['total_likes'] = Like.objects.count()
    post['total_favorites'] = Favorite.objects.count()

    return Response(post, status=200)




@api_view(['GET'])
def author_statistics(request):
    users = User.objects.annotate(
        posts_count=Count('post'),
        total_views=Sum('post__views'),
        average_views=Avg('post__views'),
        likes_received=Count('post__like', distinct=True)
    ).values(
        'id',
        'username',
        'posts_count',
        'total_views',
        'average_views',
        'likes_received'
    )

    return Response(users, status=200)


@extend_schema(
    methods=['GET'],
    responses={200: UserSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    request=UserSerializer,
    responses={201: UserSerializer}
)
@api_view(['GET','POST'])
def likes(request):
    if request.method == 'GET':
        like = Like.objects.select_related('user', 'post').all()
        serializer = LikeSerializer(like, many=True)
        return Response(serializer.data, status=200)
    
    if request.method == 'POST':
        serializer = LikeCreateSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)




# @extend_schema(
#     methods=['DELETE'],
#     responses={204: None}
# )
@api_view(['DELETE'])
def like_delete(request, id):
    try:
        like = Like.objects.get(id=id)
    except Like.DoesNotExist:
        return Response({'error': 'Лайк не найден'}, status=404)

    like.delete()
    return Response({'message': 'Лайк удалён'}, status=200)


@api_view(['GET'])
def post_likes(request, id):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return Response({'error': 'Публикация не найдена'}, status=404)

    like = Like.objects.filter(post=post)
    users = User.objects.filter(like__post=post).distinct()

    serializer = PostLikeUserSerializer(users, many=True)

    return Response({
        'post_id': post.id,
        'likes_count': like.count(),
        'users': serializer.data
    }, status=200)
    
    
@api_view(['GET'])
def top_posts_likes(request):
    post = Post.objects.annotate(
        likes_count=Count('like')
    ).order_by('-likes_count')[:10]

    serializer = TopPostLikeSerializer(post, many=True)
    return Response(serializer.data, status=200)


@extend_schema(
    methods=['GET'],
    responses={200: FavoriteSerializer(many=True)}
)
@extend_schema(
    methods=['POST'],
    request=FavoriteCreateSerializer,
    responses={201: FavoriteCreateSerializer, 400: None}
)
@api_view(['GET', 'POST'])
def favorites(request):
    if request.method == 'GET':
        favorite = Favorite.objects.select_related(
            'user', 'post', 'post__user'
        ).annotate(
            likes_count=Count('post__like', distinct=True)
        )

        serializer = FavoriteSerializer(favorite, many=True)
        return Response(serializer.data, status=200)

    serializer = FavoriteCreateSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def favorite_delete(request, id):
    try:
        favorite = Favorite.objects.get(id=id)
    except Favorite.DoesNotExist:
        return Response({'error': 'Избранное не найдено'}, status=404)

    favorite.delete()
    return Response({'message': 'Удалено из избранного'}, status=200)



@extend_schema(
    responses={200: UserFavoritesSerializer}
)
@api_view(['GET'])
def user_favorites(request, id):
    try:
        user = User.objects.annotate(
            favorites_count=Count('favorite')
        ).get(id=id)
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=404)

    serializer = UserFavoritesSerializer(user)
    return Response(serializer.data, status=200)




@extend_schema(
    responses={200: dict}
)
@api_view(['GET'])
def user_analytics(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=404)

    posts = Post.objects.filter(user=user)
    favorites = Favorite.objects.filter(user=user)
    likes_given = Like.objects.filter(user=user)

    seven_days_ago = timezone.now() - timedelta(days=7)
    posts_last_7_days = posts.filter(created_at__gte=seven_days_ago).count()

    data = {
        'user': AnalyticsUserSerializer(user).data,
        'posts': {
            'posts_count': posts.count(),
            'total_views': posts.aggregate(total=Sum('views'))['total'] or 0,
            'average_views': posts.aggregate(average=Avg('views'))['average'] or 0
        },
        'engagement': {
            'likes_received': Like.objects.filter(post__user=user).count(),
            'favorites_received': Favorite.objects.filter(post__user=user).count(),
            'likes_given': likes_given.count(),
            'favorites_given': favorites.count()
        },
        'activity': {
            'posts_last_7_days': posts_last_7_days,
            'is_active_user': posts_last_7_days > 0
        }
    }

    return Response(data, status=200)



@extend_schema(
    responses={200: dict}
)
@api_view(['GET'])
def dashboard(request):
    statistics = {
        'users_count': User.objects.count(),
        'profiles_count': Profile.objects.count(),
        'posts_count': Post.objects.count(),
        'likes_count': Like.objects.count(),
        'favorites_count': Favorite.objects.count(),
        'total_views': Post.objects.aggregate(total=Sum('views'))['total'] or 0,
        'average_views': Post.objects.aggregate(average=Avg('views'))['average'] or 0
    }

    most_active_user = User.objects.annotate(
        posts_count=Count('post')
    ).order_by('-posts_count').first()

    most_popular_post = Post.objects.annotate(
        likes_count=Count('like', distinct=True)
    ).order_by('-likes_count').first()

    latest_posts = Post.objects.annotate(
        likes_count=Count('like', distinct=True)
    ).select_related('user').order_by('-created_at')[:5]

    data = {
        'statistics': statistics,
        'most_active_user': None,
        'most_popular_post': None,
        'latest_posts': DashboardPostSerializer(
            latest_posts, many=True
        ).data
    }

    if most_active_user:
        data['most_active_user'] = {
            'id': most_active_user.id,
            'username': most_active_user.username,
            'posts_count': most_active_user.posts_count
        }

    if most_popular_post:
        data['most_popular_post'] = {
            'id': most_popular_post.id,
            'title': most_popular_post.title,
            'likes_count': most_popular_post.likes_count
        }

    return Response(data, status=200)
