from rest_framework import serializers
from article.models import Article, Category, Comment
from django.contrib.auth.models import User

class SubCategorySerializer(serializers.ModelSerializer):
    articles = serializers.SerializerMethodField()
    class Meta:
        model= Category
        fields = ('id','name', 'slug', 'created_at', 'articles')
        
    def get_articles(self, obj):
        articles = Article.objects.select_related('category').filter(category__slug=obj.slug).order_by('-created_at')[0:5]
        return ArticleSerializer(articles, many=True).data
    
class SubCategoryViewSerializer(serializers.ModelSerializer):
    articles = serializers.SerializerMethodField()
    class Meta:
        model= Category
        fields = ('id','name', 'slug', 'created_at', 'articles')
        
    def get_articles(self, obj):
        articles = Article.objects.select_related('category').filter(category__slug=obj.slug).order_by('-created_at')
        return ArticleSerializer(articles, many=True).data
        
class SubCategoryMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model= Category
        fields = ('id','name', 'slug', 'created_at')
        
class ArticleSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    class Meta:
        model= Article
        fields = ('id','name', 'author', 'category', 'subcategory','slug', 'summary','image','article','updated_at','time_ago')
        
    def get_category(self, obj):
        category = obj.category.parent
        return SubCategoryMiniSerializer(category).data
    
    def get_subcategory(self, obj):
        subcategory = obj.category
        return SubCategoryMiniSerializer(subcategory).data
    
class CategoryMiniSerializer(serializers.ModelSerializer):
    subcategory = serializers.SerializerMethodField()
    # url = serializers.SerializerMethodField()
    class Meta:
        model= Category
        fields = ('id','name', 'slug','subcategory')
    
    def get_subcategory(self, obj):
        subcategories = Category.objects.select_related('parent').filter(parent=obj)
        return SubCategoryMiniSerializer(subcategories, many=True).data
    
class CategorySerializer(serializers.ModelSerializer):
    articles = serializers.SerializerMethodField()
    class Meta:
        model= Category
        fields = ('id','name', 'slug','articles')
    
    def get_articles(self,obj):
        from django.db.models import Q
        articles = Article.objects.select_related('category').filter(Q(category__parent=obj) | Q(category=obj)).order_by('-created_at')[0:5]
        return ArticleSerializer(articles, many=True).data

class CategoryViewSerializer(serializers.ModelSerializer):
    subcategory = serializers.SerializerMethodField()
    # url = serializers.SerializerMethodField()
    class Meta:
        model= Category
        fields = ('id','name', 'slug', 'subcategory')
    
    def get_subcategory(self, obj):
        subcategories = Category.objects.select_related('parent').filter(parent=obj)[0:6]
        return SubCategorySerializer(subcategories, many=True).data
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)

class CommentParentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'replies'
        ]
        
class RecursiveCommentSerializer(serializers.ModelSerializer):
    # replies = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    parent = CommentParentSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = [
            'id',
            # 'article',
            'user',
            'content',
            'created_at',
            'replies',
            'parent'
        ]

    # def get_replies(self, obj):
    #     if obj.replies.exists():
    #         # return RecursiveCommentSerializer(obj.replies.all(), many=True).data
    #         return obj.replies.all()
    #     return []

class CommentSerializer(serializers.ModelSerializer):
    # replies = RecursiveCommentSerializer(many=True, read_only=True)
    # replies = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(read_only=True)
    # parent = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = [
            'id',
            'article',
            'user',
            'content',
            'parent',
            'created_at',
            'replies'
        ]
        read_only_fields = ['replies']
            
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

