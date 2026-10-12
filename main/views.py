from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from django.db.models import Count,Avg, Min, Max,Case, When, Value, BooleanField
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from django.db.models import Q

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
        204: None
    }
)
@api_view(['GET','PUT','PATCH','DELETE'])
def users_id(request,id):
    if request.method == 'GET':
        user = User.objects.get(id=id)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
    if request.method == 'PUT':
        user = User.objects.get(id=id)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors, status=400)
    if request.method == 'PATCH':
        user = User.objects.get(id=id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
    if request.method == 'DELETE':
        user = User.objects.get(id=id)
        user.delete()
        return Response(status=204)
    

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
        204: None
    }
)
@api_view(['GET','PUT','PATCH','DELETE'])
def profiles_id(request,id):
    if request.method == 'GET':
        profile = Profile.objects.get(id=id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data,status=200)
    
    if request.method == 'PUT':
        profile = Profile.objects.get(id=id)
        serializer = ProfileSerializer(profile, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=400)
    
    if request.method == 'PATCH':
        profile = Profile.objects.get(id=id)
        serializer = ProfileSerializer(profile, data= request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=200)
        return Response(serializer.errors,status=400)
    
    if request.method == 'DELETE':
        profile = Profile.objects.get(id=id)
        profile.delete()
        return Response(status=204)
    
    

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
        min_views=Min('views'),
        total_likes=Count('like', distinct=True),
        total_favorites=Count('favorite', distinct=True)
    )

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


@api_view(['GET'])
def likes(request):
    like = Like.objects.select_related('user', 'post').all()
    serializer = LikeSerializer(like, many=True)
    return Response(serializer.data, status=200)