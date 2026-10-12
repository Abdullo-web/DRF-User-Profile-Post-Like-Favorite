from rest_framework import serializers
from .models import *
from django.db.models import Sum,Count



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
      
class PostUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'  
        
class PostSerializer(serializers.ModelSerializer):
    author = PostUserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(),
        source = 'user',
        write_only = True
    )
    likes_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    is_popular = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Post
        fields = ['id','title','content','author','author_id','views','likes_count','favorites_count','is_popular','created_at']
       
class PostDetailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
 
 
class PostDetailSerializer(serializers.ModelSerializer):
    author = PostDetailUserSerializer(source='user', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    liked_by = PostDetailUserSerializer(source='user.like_set', many=True, read_only=True)
    favorited_by = PostDetailUserSerializer(source='user.favorite_set', many=True, read_only=True)
    is_popular = serializers.BooleanField(read_only=True)
    is_viral = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id','title','content','author','views','likes_count','favorites_count','liked_by','favorited_by','is_popular','is_viral','status']
        
    def get_liked_by(self, obj):
        users = User.objects.filter(like__post=obj).distinct()
        return PostDetailUserSerializer(users, many=True).data
    
    def get_favorited_by(self, obj):
        users = User.objects.filter(favorite__post=obj).distinct()
        return PostDetailUserSerializer(users, many=True).data
    
    def get_is_popular(self, obj):
        return obj.likes_count >= 10 
        
    def get_is_viral(self, obj):
        return obj.views >= 1000

    def get_status(self, obj):
        if obj.likes_count > 0:
            return 'has_likes'
        return 'no_likes'
    
    
    
class UserPostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UserPostItemSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'likes_count', 'views']
    
    
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id','user','post','created_at']
        
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id','user','post','created_at']
        
        
class PopularPostSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    is_popular = serializers.BooleanField(read_only = True)
    
        
    class Meta:
        model = Post
        fields = ['id', 'title', 'likes_count', 'favorites_count', 'is_popular']
        
        
class PostSearchSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    favorites_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'views', 'likes_count', 'favorites_count']
        
        
class LikeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title']


class LikeSerializer(serializers.ModelSerializer):
    user = LikeUserSerializer(read_only=True)
    post = LikePostSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        
        
class LikeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        if Like.objects.filter(user=data['user'], post=data['post']).exists():
            raise serializers.ValidationError('Вы уже поставили лайк этой публикации.')
        return data
    
    
class PostLikeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        
        
class TopPostLikeSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField(source='id')
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['post_id', 'title', 'likes_count']
        
        


class FavoriteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class FavoritePostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='user.username', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'author', 'likes_count']


class FavoriteSerializer(serializers.ModelSerializer):
    user = FavoriteUserSerializer(read_only=True)
    post = FavoritePostSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'post', 'created_at']
        
        
class FavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        if Favorite.objects.filter(user=data['user'], post=data['post']).exists():
            raise serializers.ValidationError(
                'Эта публикация уже есть в избранном.'
            )
        return data
    
    

class UserFavoritePostSerializer(serializers.ModelSerializer):
    post_id = serializers.IntegerField(source='post.id', read_only=True)
    title = serializers.CharField(source='post.title', read_only=True)
    views = serializers.IntegerField(source='post.views', read_only=True)
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Favorite
        fields = ['post_id', 'title', 'likes_count', 'views']


class UserFavoritesSerializer(serializers.ModelSerializer):
    favorites_count = serializers.IntegerField(read_only=True)
    results = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'favorites_count', 'results']

    def get_results(self, obj):
        favorites = Favorite.objects.filter(user=obj).select_related('post').annotate(
            likes_count=Count('post__like', distinct=True)
        )
        return UserFavoritePostSerializer(favorites, many=True).data

