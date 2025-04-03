import os
import logging
import subprocess
import django_rq
from django.conf import settings
from .models import Video

logger = logging.getLogger(__name__)
FFMPEG_PATH = '/usr/bin/ffmpeg'
AUDIO = ['-c:a', 'aac', '-ar', '48000']
VIDEO = ['-c:v', 'h264', '-profile:v', 'main', '-crf', '23', '-preset', 'veryfast']
HLS = ['-hls_time', '4', '-hls_playlist_type', 'vod']

RESOLUTIONS = [
    ("640x360", "360p", "600000"),
    ("854x480", "480p", "1000000"),
    ("1280x720", "720p", "2500000"),
]

@django_rq.job('low')
def generate_video_thumbnail_job(source, video_id):
    path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', f'{video_id}.jpg')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cmd = [FFMPEG_PATH, '-y', '-i', source, '-ss', '00:00:10.000', '-vframes', '1', path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        Video.objects.filter(id=video_id).update(thumbnail=os.path.join('thumbnails', f'{video_id}.jpg'))

@django_rq.job('low')
def generate_video_teaser(source, video_id):
    path = os.path.join(settings.MEDIA_ROOT, 'teasers', f'{video_id}_teaser.mp4')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cmd = [FFMPEG_PATH, '-y', '-i', source, '-t', '10', '-an',
           '-c:v', 'libx264', '-crf', '28', '-preset', 'veryfast', '-b:v', '500k', path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        Video.objects.filter(id=video_id).update(teaser_file=os.path.join('teasers', f'{video_id}_teaser.mp4'))

def build_hls_command(source, res, name, bitrate, out_dir):
    segment_path = os.path.join(out_dir, f'{name}_%03d.ts')
    playlist = os.path.join(out_dir, f'{name}.m3u8')
    scale = ['-vf', f'scale={res}']
    return [FFMPEG_PATH, '-i', source] + scale + AUDIO + VIDEO + \
           ['-b:v', bitrate, '-maxrate', bitrate, '-bufsize', str(int(bitrate)*2),
            '-hls_segment_filename', segment_path] + HLS + [playlist]

@django_rq.job('low')
def convert_to_hls(source, output_dir, video_id):
    base = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_id))
    os.makedirs(base, exist_ok=True)
    for res, name, bitrate in RESOLUTIONS:
        cmd = build_hls_command(source, res, name, bitrate, base)
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            logger.error(f"HLS error [{name}]: {e}")

    write_master_playlist(base, video_id)

def write_master_playlist(output_dir, video_id):
    path = os.path.join(output_dir, 'master.m3u8')
    with open(path, 'w') as f:
        f.write("#EXTM3U\n")
        for res, name, bitrate in RESOLUTIONS:
            f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate},RESOLUTION={res}\n{name}.m3u8\n")
    Video.objects.filter(id=video_id).update(hls_playlist=os.path.join('hls', str(video_id), 'master.m3u8'))

@django_rq.job('low')
def update_video_status(video_id):
    Video.objects.filter(id=video_id).update(status='Done')
