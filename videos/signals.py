import os
import shutil
import django_rq
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Video
from .tasks import (
    convert_to_hls,
    generate_video_teaser,
    generate_video_thumbnail_job,
    update_video_status,
)

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
        source = instance.video_file.path
        instance.status = 'Uploading'
        instance.save(update_fields=['status'])

        queue = django_rq.get_queue('low', autocommit=True)

        # Thumbnail zuerst
        thumbnail_job = queue.enqueue(generate_video_thumbnail_job, source, instance.id)

        # Dann Teaser, abhängig von Thumbnail
        teaser_job = queue.enqueue(generate_video_teaser, source, instance.id, depends_on=thumbnail_job)

        # Dann HLS, abhängig von Teaser
        hls_job = queue.enqueue(convert_to_hls, source, None, instance.id, depends_on=teaser_job)

        # Dann Status-Update, abhängig von HLS
        queue.enqueue(update_video_status, instance.id, depends_on=hls_job)


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    # Originalvideo löschen
    if instance.video_file and os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)

    # HLS-Dateien löschen
    hls_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(instance.id))
    if os.path.isdir(hls_dir):
        shutil.rmtree(hls_dir)

    # Thumbnail löschen
    if instance.thumbnail:
        path = os.path.join(settings.MEDIA_ROOT, instance.thumbnail.name)
        if os.path.isfile(path):
            os.remove(path)

    # Teaser löschen
    if instance.teaser_file:
        path = os.path.join(settings.MEDIA_ROOT, instance.teaser_file.name)
        if os.path.isfile(path):
            os.remove(path)
