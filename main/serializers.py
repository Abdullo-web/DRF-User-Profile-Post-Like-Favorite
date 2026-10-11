from rest_framework import serializers
from .models import *
from django.db.models import Sum



class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    posts_count = serializers.IntegerField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id','username','first_name','last_name','full_name','age','posts_count','likes_count','favorites_count']
        
        
    def get_full_name(self,obj):
        return f'{obj.first_name} {obj.last_name}'


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    statistics = serializers.SerializerMethodField()
    
    
    class Meta:
            model = User
            fields = ['id','username','full_name','age','profile','statistics']
    
    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'
    
    def get_profile(self, obj):
        try:
            profile = obj.profile
            return {
                'bio': profile.bio,
                'city': profile.city
                }
        except Profile.DoesNotExist:
            return None
        
    def get_statistics(self,obj):
        posts = obj.post_set.all()
        
        return {
            'posts_count': posts.count(),
            'total_views': posts.aggregate(total=Sum('views'))['total'] or 0,
            'likes_received': Like.objects.filter(post__user=obj).count(),
            'favorites_received': Favorite.objects.filter(post__user=obj).count()
        }
            
class ProfileUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']
        
    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'


class ProfileSerializer(serializers.ModelSerializer):
    user = ProfileUserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    posts_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id','user','user_id','bio','city','birth_date','avatar','posts_count']
        
        
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id','user','title','content','views','created_at','updated_at']
        
        
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id','user','post','created_at']
        
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id','user','post','created_at']