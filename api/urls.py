from django.urls import path
from .import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
urlpatterns = [
    path('articleApi/', views.ArticleApi),
    path('articleViewApi/', views.ArticleViewApi),
    path('categoryApi/', views.CategoryApi),
    path('categoryarticleApi/', views.CategoryArticleApi),
    path('checkUrl/', views.CheckUrlApi),
    path('search/', views.SearchAPi),
    
    path('createcomments/', views.CommentCreateAPIView.as_view(), name='comment-create'),
    path('listcomments/', views.CommentListAPIView.as_view(), name='comment-list'),
    path('listrepliescomment/', views.CommentRepliesListAPIView.as_view(), name='comment-replies-list'),
    
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/', views.UserDetailView.as_view(), name='user_detail'),
    path('google/validate_token/', views.validate_google_token, name='validate_token'),
    path('user/register/', views.UserCreate.as_view()),
]
