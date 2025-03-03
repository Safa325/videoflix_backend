from django.contrib import admin
from django.db import transaction
from .models import Video, Category

class VideoAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        if is_new and obj.video_file:
            from .signals import video_post_save
            transaction.on_commit(lambda: video_post_save(Video, obj, created=True))

admin.site.register(Video, VideoAdmin)

admin.site.register(Category)