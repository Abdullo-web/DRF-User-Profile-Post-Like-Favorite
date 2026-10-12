from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from django.db.models import Count,Avg, Min, Max,Case, When, Value, BooleanField
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes


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