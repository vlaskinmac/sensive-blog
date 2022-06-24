from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count


class PostQuerySet(models.QuerySet):

    def year(self, year):
        posts_at_year = self.filter(published_at__year=year).order_by('published_at')
        return posts_at_year

    def popular(self):
        popular_posts = Post.objects.prefetch_related('author').annotate(
            quantity_likes=Count('likes')).order_by('-quantity_likes')[:5]
        return popular_posts

    def fetch_with_comments_count(self):
        popular_posts = self.popular()
        popular_posts_ids = [post.id for post in popular_posts]
        posts_with_comments = Post.objects.prefetch_related('author').filter(
            id__in=popular_posts_ids).annotate(quantity_comments=Count('comments'))
        return posts_with_comments


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')
    objects = PostQuerySet.as_manager()

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class TagQuerySet(models.QuerySet):

    def popular_tags(self):
        popular_tags = self.prefetch_related('posts').annotate(quantity_posts=Count('posts')).order_by('-quantity_posts')[:5]
        return popular_tags


class Tag(models.Model):
    objects = TagQuerySet.as_manager()

    title = models.CharField('Тег', max_length=20, unique=True)

    def __str__(self):
        return self.title

    def clean(self):
        self.title = self.title.lower()

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        verbose_name='Пост, к которому написан', related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор')

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'


