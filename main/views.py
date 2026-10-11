from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *


@api_view(['GET'])
def users(request):
    user = User.objects.all()
    serializer = UserSerializer(user, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def users_id(request,id):
    user = User.objects.get(id=id)
    serializer = UserSerializer(user)
    return Response(serializer.data)