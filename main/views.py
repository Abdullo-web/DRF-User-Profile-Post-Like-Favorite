from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from django.db.models import Count,Avg, Min, Max

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



@api_view(['GET', 'POST'])
def profiles(request):
    if request.method == 'GET':
        profile = Profile.objects.all()
        serializer = ProfileSerializer(profile, many=True)
        return Response(serializer.data, status=200)

    if request.method == 'POST':
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
