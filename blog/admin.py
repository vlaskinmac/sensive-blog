from django.contrib import admin
from blog.models import Post, Tag, Comment


admin.site.register(Tag)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ('likes','tags')


@admin.register(Comment)
class TagAdmin(admin.ModelAdmin):
    raw_id_fields = ('author',)
    list_display = ['post', 'author',]