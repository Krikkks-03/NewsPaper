from django.shortcuts import render, get_object_or_404

# Create your views here.
from .models import Post

def news_list(request):
    posts = Post.objects.order_by('-created_at')
    return render(request, 'news/news_list.html', {'articles': posts})

def news_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'news/news_detail.html', {'article': post})