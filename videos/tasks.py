import os
import logging
import subprocess
import django_rq

from django.conf import settings
from .models import Video

logger = logging.getLogger(__name__)

FFMPEG_PATH = '/usr/bin/ffmpeg'
AUDIO_PARAMS = ['-c:a', 'aac', '-ar', '48000']
VIDEO_CODEC = ['-c:v', 'h264', '-profile:v', 'main', '-crf', '20', '-g', '48', '-keyint_min', '48']
HLS_PARAMS = ['-hls_time', '4', '-hls_playlist_type', 'vod']

RESOLUTIONS = [
    ("1280x720", "720p", "2500000"),
    ("854x480", "480p", "1000000"),
    ("640x360", "360p", "600000"),
]

@django_rq.job('low')
def generate_video_thumbnail_job(source, video_id):
    try:
        thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
        os.makedirs(thumbnail_dir, exist_ok=True)
        thumbnail_path = os.path.join(thumbnail_dir, f'{video_id}.jpg')
        cmd = [FFMPEG_PATH, '-y', '-i', source, '-ss', '00:00:10.000', '-vframes', '1', thumbnail_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            logger.error(f"❌ Error generating thumbnail: {result.stderr.decode('utf-8')}")
            return

        video = Video.objects.get(id=video_id)
        video.thumbnail = os.path.join('thumbnails', f'{video_id}.jpg')
        video.save(update_fields=['thumbnail'])

    except Exception as e:
        logger.exception(f"Fehler im Thumbnail-Job: {e}")

@django_rq.job('low')
def generate_video_teaser(source, video_id):
    try:
        teaser_dir = os.path.join(settings.MEDIA_ROOT, 'teasers')
        os.makedirs(teaser_dir, exist_ok=True)
        teaser_path = os.path.join(teaser_dir, f'{video_id}_teaser.mp4')

        cmd = [
            FFMPEG_PATH, '-y', '-i', source,
            '-t', '10', '-an',
            '-c:v', 'libx264', '-crf', '28', '-preset', 'veryfast',
            '-b:v', '500k', teaser_path
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"❌ Error generating teaser: {result.stderr.decode('utf-8')}")
            return

        video = Video.objects.get(id=video_id)
        video.teaser_file = os.path.join('teasers', f'{video_id}_teaser.mp4')
        video.save(update_fields=['teaser_file'])

    except Exception as e:
        logger.exception(f"Fehler beim Teaser-Export: {e}")

@django_rq.job('low')
def convert_to_hls(source, output_dir, video_id):
    try:
        output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_id))
        os.makedirs(output_dir, exist_ok=True)

        for res, name, bitrate in RESOLUTIONS:
            output_path = os.path.join(output_dir, f'{name}.m3u8')
            segment_path = os.path.join(output_dir, f'{name}_%03d.ts')
            scale_filter = f"scale={res}"

            cmd = [
                FFMPEG_PATH, '-i', source,
                '-vf', scale_filter,
                *AUDIO_PARAMS,
                *VIDEO_CODEC,
                '-b:v', bitrate, '-maxrate', bitrate, '-bufsize', str(int(bitrate) * 2),
                '-hls_segment_filename', segment_path,
                *HLS_PARAMS,
                output_path
            ]

            subprocess.run(cmd, check=True)

        master_playlist_path = os.path.join(output_dir, 'master.m3u8')
        with open(master_playlist_path, 'w') as f:
            f.write("#EXTM3U\n")
            for res, name, bitrate in RESOLUTIONS:
                f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate},RESOLUTION={res}\n")
                f.write(f"{name}.m3u8\n")

        video = Video.objects.get(id=video_id)
        video.hls_playlist = os.path.join('hls', str(video_id), 'master.m3u8')
        video.save(update_fields=['hls_playlist'])

    except Exception as e:
        logger.exception(f"❌ Fehler bei der HLS-Konvertierung: {e}")

@django_rq.job('low')
def update_video_status(video_id):
    try:
        video = Video.objects.get(id=video_id)
        video.status = 'Done'
        video.save(update_fields=['status'])
    except Exception as e:
        logger.exception(f"❌ Fehler beim Status-Update: {e}")
