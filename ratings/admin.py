from django.contrib import admin

from .models import Comment, Review, Title


class TitleAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "year", "description")
    search_fields = ()
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "title")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "review")
    search_fields = ("text",)
    empty_value_display = "-пусто-"


admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
