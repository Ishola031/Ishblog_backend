from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timesince import timesince
from django.utils import timezone


# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    avatar = models.URLField(blank=True, null=True)  # Google profile pic URL

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories'
    )
    description = models.TextField(max_length=70, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'categories'
        
    # def get_url(self):
    #     return reverse("api.category", kwargs={"category": self.slug})
    
    def __str__(self):
        return self.name

class Article(models.Model):
    name = models.CharField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    slug = models.SlugField()
    image = models.ImageField(upload_to='ArticleImage')
    summary = models.CharField(default='')
    article = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def time_ago(self):
        time_str = timesince(self.created_at, timezone.now())
        return time_str.split(",")[0] + " ago"
    
    def __str__(self):
        return self.name
    
class ArticleView(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.article.name)
    

class Comment(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=timezone.now)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies'
    )

    def __str__(self):
        return f"{self.user.username} on {self.article.name}: {self.content[0:20]}"

    class Meta:
        ordering = ['-created_at']
        
    @property
    def time_ago(self):
        time_str = timesince(self.created_at, timezone.now())
        return time_str.split(",")[0] + " ago"
        
