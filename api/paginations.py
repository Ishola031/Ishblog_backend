from rest_framework.pagination import PageNumberPagination

class CommentPagination(PageNumberPagination):
    page_size = 6
    
class ArticlePagination(PageNumberPagination):
    page_size = 8