# articles/urls.py
from django.urls import path
from .views import (
    ArticleListView,
    ArticleDetailView,
    ArticleUpdateView,
    ArticleDeleteView,
    ArticleCreateView,
    CommentCreateView,
    CommentUpdateView,
    CommentDeleteView,
    upload_image,
    delete_image,
)

urlpatterns = [
    path("", ArticleListView.as_view(), name="article_list"),
    path("<int:pk>/", ArticleDetailView.as_view(), name="article_detail"),
    path("<int:pk>/edit/", ArticleUpdateView.as_view(), name="article_edit"),
    path("<int:pk>/delete/", ArticleDeleteView.as_view(), name="article_delete"),
    path("new/", ArticleCreateView.as_view(), name="article_new"),
    path("<int:pk>/comment/", CommentCreateView.as_view(), name="comment_new"),
    path("comment/<int:pk>/edit/", CommentUpdateView.as_view(), name="comment_edit"),
    path("comment/<int:pk>/delete/", CommentDeleteView.as_view(), name="comment_delete"),
    path('articles/<int:pk>/upload_image/', upload_image, name='upload_image'),
    path('articles/<int:pk>/delete_image/<str:image_id>/', delete_image, name='delete_image'),
]