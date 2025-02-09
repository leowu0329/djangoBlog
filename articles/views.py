from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.views import View
from django.views.generic import ListView, DetailView, FormView  # new
from django.views.generic.detail import SingleObjectMixin  # new
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy, reverse  # new
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import cloudinary
import cloudinary.uploader
import cloudinary.api

from .forms import CommentForm
from .models import Article,Comment


class ArticleListView(LoginRequiredMixin, ListView):  # new
    model = Article
    template_name = "article_list.html"


class CommentGet(DetailView):  # new
    model = Article
    template_name = "article_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        return context


class CommentPost(SingleObjectMixin, FormView):  # new
    model = Article
    form_class = CommentForm
    template_name = "article_detail.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.article = self.object
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        article = self.object
        return reverse("article_detail", kwargs={"pk": article.pk})

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    fields = ('title', 'body',)
    template_name = 'article_edit.html'

    def test_func(self):  # 新增
        obj = self.get_object()
        return obj.author == self.request.user

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'article_delete.html'
    success_url = reverse_lazy('article_list')

    def test_func(self):  # 新增
        obj = self.get_object()
        return obj.author == self.request.user

class ArticleDetailView(LoginRequiredMixin, View):  # new
    def get(self, request, *args, **kwargs):
        view = CommentGet.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CommentPost.as_view()
        return view(request, *args, **kwargs)


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):  # new
    model = Article
    fields = (
        "title",
        "body",
    )
    template_name = "article_edit.html"

    def test_func(self):  # new
        obj = self.get_object()
        return obj.author == self.request.user


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):  # new
    model = Article
    template_name = "article_delete.html"
    success_url = reverse_lazy("article_list")

    def test_func(self):  # new
        obj = self.get_object()
        return obj.author == self.request.user


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    template_name = "article_new.html"
    fields = (
        "title",
        "body",
    )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = "comment_new.html"
    fields = ("comment",)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.article = Article.objects.get(pk=self.kwargs["pk"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("article_detail", kwargs={"pk": self.kwargs["pk"]})

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ("comment",)
    template_name = "comment_edit.html"

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def get_success_url(self):
        article = self.object.article
        return reverse("article_detail", kwargs={"pk": article.pk})

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "comment_delete.html"

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def get_success_url(self):
        article = self.object.article
        return reverse("article_detail", kwargs={"pk": article.pk})

@login_required
def upload_image(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user != article.author:
        messages.error(request, "您沒有權限上傳圖片")
        return redirect('article_detail', pk=pk)
    
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            result = cloudinary.uploader.upload(
                request.FILES['image'],
                folder=f'django-blog/articles/{pk}/',
                resource_type="image"
            )
            messages.success(request, "圖片上傳成功")
        except Exception as e:
            messages.error(request, f"圖片上傳失敗：{str(e)}")
    
    return redirect('article_detail', pk=pk)

@login_required
def delete_image(request, pk, image_id):
    article = get_object_or_404(Article, pk=pk)
    if request.user != article.author:
        messages.error(request, "您沒有權限刪除圖片")
        return redirect('article_detail', pk=pk)
    
    if request.method == 'POST':
        try:
            cloudinary.uploader.destroy(image_id)
            messages.success(request, "圖片刪除成功")
        except Exception as e:
            messages.error(request, f"圖片刪除失敗：{str(e)}")
    
    return redirect('article_detail', pk=pk)

class ArticleDetailView(DetailView):
    model = Article
    template_name = "article_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        
        # 獲取文章的所有圖片
        try:
            result = cloudinary.api.resources(
                prefix=f'django-blog/articles/{self.object.pk}/',
                type='upload',
                max_results=100
            )
            context['images'] = result.get('resources', [])
        except Exception as e:
            print(f"Error fetching images: {e}")
            context['images'] = []
            
        return context
