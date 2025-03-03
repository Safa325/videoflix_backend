import os
import shutil

import django_rq
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Video
from .tasks import (convert_to_hls, generate_video_teaser,
                    generate_video_thumbnail, update_video_status, write_master_playlist)
from .tasks import RESOLUTIONS


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal-Handler, der nach dem Speichern eines `Video`-Objekts ausgelöst wird.

    Falls ein neues Video hochgeladen wurde, wird:
    - Ein Thumbnail generiert.
    - Der Status auf "Uploading" gesetzt.
    - Das Video in verschiedene HLS-Auflösungen umgewandelt.
    - Ein Teaser-Clip erstellt.
    - Der HLS-Playlist-Pfad gespeichert.

    :param sender: Modellklasse (`Video`)
    :param instance: Die Instanz des `Video`-Modells
    :param created: Bool, ob das Objekt neu erstellt wurde
    :param kwargs: Zusätzliche Argumente
    """
    if created and instance.video_file:
        source = instance.video_file.path

        # Verzeichnis für HLS-Streaming-Dateien
        output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(instance.id))

        # Generiere ein Thumbnail für das Video
        thumbnail_relative_path = generate_video_thumbnail(instance.video_file.path, instance.id)
        instance.thumbnail = thumbnail_relative_path
        instance.save(update_fields=['thumbnail'])

        # Setze den Status auf "Uploading"
        instance.status = 'Uploading'
        instance.save(update_fields=['status'])

        # Hintergrund-Queue für HLS-Umwandlung & Teaser-Generierung
        queue = django_rq.get_queue('low', autocommit=True)
        hls_job = queue.enqueue(convert_to_hls, source, output_dir, instance.id)
        hls_master = queue.enqueue(write_master_playlist, output_dir, RESOLUTIONS)
        teaser_job = queue.enqueue(generate_video_teaser, instance.video_file.path, instance.id)

        # HLS-Playlist & Teaser-Pfade in der Datenbank speichern
        hls_playlist_url = os.path.join('hls', str(instance.id), 'master.m3u8')
        instance.hls_playlist = hls_playlist_url
        instance.teaser_file = os.path.join('teasers', f'{instance.id}_teaser.mp4')
        instance.save(update_fields=['hls_playlist', 'teaser_file'])

        # Sobald die HLS-Umwandlung & der Teaser fertig sind → Status auf "Done" setzen
        queue.enqueue(update_video_status, instance.id, depends_on=[hls_job, teaser_job, hls_master])


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Signal-Handler, der nach dem Löschen eines `Video`-Objekts ausgelöst wird.

    Falls ein Video gelöscht wird, werden:
    - Die Videodatei entfernt.
    - Die HLS-Streaming-Dateien gelöscht.
    - Das Thumbnail & der Teaser gelöscht.

    :param sender: Modellklasse (`Video`)
    :param instance: Die Instanz des `Video`-Modells
    :param kwargs: Zusätzliche Argumente
    """
    # Original-Videodatei entfernen
    if instance.video_file and os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)

    # HLS-Streaming-Dateien entfernen
    hls_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(instance.id))
    if os.path.isdir(hls_dir):
        shutil.rmtree(hls_dir)

    # Thumbnail entfernen
    if instance.thumbnail and os.path.isfile(instance.thumbnail.path):
        os.remove(instance.thumbnail.path)

    # Teaser-Datei entfernen
    if instance.teaser_file and os.path.isfile(instance.teaser_file.path):
        os.remove(instance.teaser_file.path)
