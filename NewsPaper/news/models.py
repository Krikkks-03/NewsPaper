from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):

        post_rating = Post.objects.filter(author=self).aggregate(pr=Sum('rating'))['pr'] or 0
        post_rating *= 3

        # суммарный рейтинг всех комментариев автора
        comment_rating = Comment.objects.filter(user=self.user).aggregate(cr=Sum('rating'))['cr'] or 0

        posts = Post.objects.filter(author=self)
        posts_comments_rating = Comment.objects.filter(post__in=posts).aggregate(pcr=Sum('rating'))['pcr'] or 0

        self.rating = post_rating + comment_rating + posts_comments_rating
        self.save()

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subscribers')
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category')  # чтобы пользователь не подписался дважды

        def __str__(self):
            return f'{self.user.username} -> {self.category.name}'

class Post(models.Model):
    ARTICLE = 'article'
    NEWS = 'news'
    TYPE_CHOICES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=ARTICLE)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=200)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    categories = models.ManyToManyField(Category, through='PostCategory')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        # возвращает начало статьи
        return self.text[:124] + '...' if len(self.text) > 124 else self.text

    def __str__(self):
        return f'{self.title} ({self.get_type_display()})'

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'