from django.shortcuts import get_object_or_404, redirect
from .serializers import  ArticleSerializer, CategorySerializer,CategoryMiniSerializer, CategoryViewSerializer, CommentSerializer,RecursiveCommentSerializer, UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from article.models import Article, Category, Comment
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import ListAPIView
from .paginations import CommentPagination, ArticlePagination
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Count, F, Q


User = get_user_model()


# Create your views here.
#///////////////////////////////
# API
# /////////////////////////////
class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
@login_required
def google_login_callback(request):
    user = request.user
    
    social_accounts = SocialAccount.objects.filter(user=user)
    
    social_account = social_accounts.first()
    
    if not social_account:
        print("No social account for user", user)
        return redirect('http://localhost:5173/login/callback/?error=NoSocialAccount')
    token = SocialToken.objects.select_related('account').filter(account=social_account, account__provider='google').first()
    if token:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return redirect(f'http://localhost:5173/login/callback/?access_token={access_token}')
    else:
        print('No Google token found for user', user)
        return redirect(f'http://localhost:5173/login/callback/?error=NoGoogleToken')

@csrf_exempt
def validate_google_token(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            google_access_token = data.get('access_token')
                        
            if not google_access_token:
                return JsonResponse({'detail': 'Access Token is missing.'}, status=400)
            return JsonResponse({'valid': True})
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid JSON'}, status=400)
    return JsonResponse({'detail': 'Method not allowed.'}, status=405)
        
@api_view(['GET'])
@permission_classes([AllowAny])
def ArticleApi(request):
    articles = Article.objects.select_related('category')\
        .prefetch_related('category__subcategories').order_by('-created_at')
    paginator = ArticlePagination()
    page = paginator.paginate_queryset(articles, request)
    serializer = ArticleSerializer(page, many=True, context={'request': request})
    return Response({
        "count": paginator.page.paginator.count,
        "next": paginator.get_next_link(),
        "previous": paginator.get_previous_link(),
        "results": serializer.data
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def CategoryApi(request):
    categories = Category.objects.filter(parent=None).order_by('-created_at')
    serializer= CategoryMiniSerializer(categories, many=True,context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def CategoryArticleApi(request, slug=None):
    slug = request.GET.get('slug', None)
    if slug:
        category = get_object_or_404(Category, slug=slug)
        articles = Article.objects.filter(category__slug=slug).select_related('category').order_by('-updated_at')
        paginator = ArticlePagination()
        page = paginator.paginate_queryset(articles, request)
        serializer = ArticleSerializer(page, many=True)
        
        return Response({
            "category": CategoryViewSerializer(category).data,
            # "subcategories": CategoryViewSerializer(),
            "articles": {
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": serializer.data
            }
        })
        
    else:
        categories = Category.objects.filter(parent=None).annotate(
            category_count=Count(
                'articles', distinct=True
            ),
            subcategorycount = Count(
                'subcategories__articles',
                distinct=True
            )
        ).annotate(articles_count=F('category_count') + F('subcategorycount')).filter(articles_count__gt=0).order_by('-created_at')
        print(categories.values('name', 'category_count', 'subcategorycount', 'articles_count'))
        serializer= CategorySerializer(categories, many=True,context={'request': request})
        return Response(serializer.data)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def ArticleViewApi(request, articleslug=None):
    articleslug = request.GET.get('articleslug', None)
    if articleslug:
        article = get_object_or_404(Article, slug=articleslug)
        serializer = ArticleSerializer(article,context={'request': request})
        return Response(serializer.data)
    return Response({})

@api_view(['GET'])
@permission_classes([AllowAny])
def CheckUrlApi(request):
    slug = request.GET.get('slug', None)
    if slug:
        try:
            article = Article.objects.get(slug=slug)
            if article:
                result = 'article'
            return Response({'result':result})
        except:
            pass
        try:
            subcategory = Category.objects.get(slug=slug)
            if subcategory:
                result= 'subcategory'
            return Response({'result': result})
        except:
            pass
    return Response({'result': result})

class CommentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            comment = serializer.save(user=request.user)
            commentid = request.data.get('parent')
            
            return Response(
                CommentSerializer(comment).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentListAPIView(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]
    pagination_class= CommentPagination

    def get_queryset(self):
        slug = self.request.GET.get('articleslug')
        if not slug:
            return Comment.objects.none()

        return Comment.objects.filter(
            article__slug=slug,
            parent__isnull=True
        ).order_by('-created_at')

class CommentRepliesListAPIView(ListAPIView):
    serializer_class = RecursiveCommentSerializer
    permission_classes = [AllowAny]
    pagination_class = CommentPagination

    def get_queryset(self):
        slug = self.request.GET.get('articleslug', None)
        cid = self.request.GET.get('cid')
        if not slug:
            return Comment.objects.none()
        

        return Comment.objects.filter(
            article__slug=slug,
            parent__id=cid
        ).order_by('-created_at')

@api_view(['GET'])
@permission_classes([AllowAny])
def SearchAPi(request):
    searchValue = request.GET.get('search', None)
    if searchValue:
        articles = Article.objects.filter(Q(name__icontains=searchValue) | Q(category__name__icontains= searchValue)).order_by('-created_at').distinct()
        paginator = ArticlePagination()
        page = paginator.paginate_queryset(articles, request)
        serializers = ArticleSerializer(page, many=True)
        return Response({
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": serializers.data
        })
    return Response('Search Input Not Provided')
