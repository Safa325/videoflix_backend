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
    ("160x120", "120p", "150000"),
    ("640x360", "360p", "600000"),
    ("854x480", "480p", "1000000"),
]

def build_absolute_url(relative_path: str) -> str:
    domain = 'videoflix.shamarisafa.ch'
    return f"https://{domain}/{relative_path.strip('/')}"

def save_video_field(video_id, field_name, relative_path):
    video = Video.objects.get(id=video_id)
    setattr(video, field_name, build_absolute_url(os.path.join('media', relative_path)))
    video.save(update_fields=[field_name])

@django_rq.job('low')
def generate_video_thumbnail_job(source, video_id):
    try:
        path = os.path.join('thumbnails', f'{video_id}.jpg')
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        cmd = [FFMPEG_PATH, '-y', '-i', source, '-ss', '00:00:10.000', '-vframes', '1', full_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"❌ Thumbnail error: {result.stderr.decode()}")
            return
        save_video_field(video_id, 'thumbnail', path)
    except Exception as e:
        logger.exception(f"Thumbnail-Job failed: {e}")

@django_rq.job('low')
def generate_video_teaser(source, video_id):
    try:
        path = os.path.join('teasers', f'{video_id}_teaser.mp4')
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        cmd = [FFMPEG_PATH, '-i', source, '-t', '10', '-an', '-c:v', 'libx264', '-crf', '28',
               '-preset', 'veryfast', '-b:v', '500k', full_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logger.error(f"❌ Teaser error: {result.stderr.decode()}")
            return
        save_video_field(video_id, 'teaser_file', path)
    except Exception as e:
        logger.exception(f"Teaser-Job failed: {e}")

def build_hls_cmd(source, res, name, bitrate, segment_path, output_path):
    scale_filter = f"scale={res}"
    return [FFMPEG_PATH, '-i', source, '-vf', scale_filter, *AUDIO_PARAMS, *VIDEO_CODEC,
            '-b:v', bitrate, '-maxrate', bitrate, '-bufsize', str(int(bitrate) * 2),
            '-hls_segment_filename', segment_path, *HLS_PARAMS, output_path]

def write_master_playlist(output_dir, video_id):
    master = os.path.join(output_dir, 'master.m3u8')
    with open(master, 'w') as f:
        f.write("#EXTM3U\n")
        for res, name, bitrate in RESOLUTIONS:
            f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate},RESOLUTION={res}\n{name}.m3u8\n")
    rel_path = os.path.join('hls', str(video_id), 'master.m3u8')
    save_video_field(video_id, 'hls_playlist', rel_path)

@django_rq.job('low')
def convert_to_hls(source, output_dir, video_id):
    try:
        output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_id))
        os.makedirs(output_dir, exist_ok=True)

        for res, name, bitrate in RESOLUTIONS:
            out_path = os.path.join(output_dir, f'{name}.m3u8')
            seg_path = os.path.join(output_dir, f'{name}_%03d.ts')
            cmd = build_hls_cmd(source, res, name, bitrate, seg_path, out_path)
            subprocess.run(cmd, check=True)

        write_master_playlist(output_dir, video_id)
    except Exception as e:
        logger.exception(f"❌ HLS error: {e}")

@django_rq.job('low')
def update_video_status(video_id):
    try:
        video = Video.objects.get(id=video_id)
        video.status = 'Done'
        video.save(update_fields=['status'])
    except Exception as e:
        logger.exception(f"❌ Status update failed: {e}")
