import os
import subprocess
import logging
from django.conf import settings
from .models import Video

logger = logging.getLogger(__name__)

FFMPEG_PATH = '/usr/bin/ffmpeg'
AUDIO_PARAMS = ['-c:a', 'aac', '-ar', '48000']
VIDEO_CODEC = ['-c:v', 'h264', '-profile:v', 'main', '-crf', '20', '-g', '48', '-keyint_min', '48']
HLS_PARAMS = ['-hls_time', '4', '-hls_playlist_type', 'vod']

RESOLUTIONS = [
    ("1920x1080", "1080p", "4500000"),
    ("1280x720", "720p", "2000000"),
    ("854x480", "480p", "1000000"),
]

def build_ffmpeg_command(source, name, bitrate, segment_path, output_path):
    """
    Erstellt den FFmpeg-Befehl zur Umwandlung des Videos in verschiedene HLS-Auflösungen.
    """
    if name == "480p":
        scale_filter = 'scale=trunc(oh*a/2)*2:480'   
    else:
        raise ValueError(f"Unbekannte Auflösung: {name}")

    return [
         FFMPEG_PATH, '-i', source,
        '-vf', scale_filter,
        *AUDIO_PARAMS,
        *VIDEO_CODEC,
        '-b:v', bitrate, '-maxrate', bitrate, '-bufsize', str(int(bitrate) * 2),
        '-hls_segment_filename', segment_path,
        *HLS_PARAMS,
        output_path
    ]

def write_master_playlist(output_dir, resolutions):
    """
    Erstellt die `master.m3u8`-Datei mit allen verfügbaren Qualitäten.
    """
    master_playlist_path = os.path.join(output_dir, 'master.m3u8')
    with open(master_playlist_path, 'w') as f:
        f.write("#EXTM3U\n")
        for res, name, bitrate in resolutions:
            f.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate},RESOLUTION={res}\n")
            f.write(f"{name}.m3u8\n")
    return master_playlist_path

def update_video_status(video_id):
    """
    Aktualisiert den Status des Videos nach der erfolgreichen HLS-Konvertierung.
    """
    video = Video.objects.get(id=video_id)
    video.status = 'Done'
    video.save(update_fields=['status'])

def convert_to_hls(source, output_dir, video_id, ):
    """
    Konvertiert ein Video in HLS-Format mit mehreren Auflösungen und erstellt eine Master-Playlist.
    """
    output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_id))
    os.makedirs(output_dir, exist_ok=True)

    for res, name, bitrate in RESOLUTIONS:
        output_path = os.path.join(output_dir, f'{name}.m3u8')
        segment_path = os.path.join(output_dir, f'{name}_%03d.ts')

        cmd = build_ffmpeg_command(source, res, name, bitrate, segment_path, output_path)

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Fehler bei {name}: {e}")
            continue
    master_file = write_master_playlist(output_dir, RESOLUTIONS)
    return master_file


def generate_video_thumbnail(source, video_id):
    """
    Erstellt eine Thumbnail-Vorschau des Videos.
    """
    thumbnail_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
    os.makedirs(thumbnail_dir, exist_ok=True)
    
    thumbnail_path = os.path.join(thumbnail_dir, f'{video_id}.jpg')
    cmd = [
        FFMPEG_PATH, '-i', source, 
        '-ss', '00:00:10.000', 
        '-vframes', '1', 
        thumbnail_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        logger.error(f"❌ Error generating thumbnail: {result.stderr.decode('utf-8')}")
        raise Exception(f"FFmpeg failed: {result.stderr.decode('utf-8')}")

    return os.path.join('thumbnails', f'{video_id}.jpg')

def generate_video_teaser(source, video_id):
    """
    Erstellt einen 10-sekündigen Teaser des Videos ohne Ton.
    """
    teaser_dir = os.path.join(settings.MEDIA_ROOT, 'teasers')
    os.makedirs(teaser_dir, exist_ok=True)

    teaser_path = os.path.join(teaser_dir, f'{video_id}_teaser.mp4')
    cmd = [
        FFMPEG_PATH, '-i', source,
        '-t', '10',
        '-an',
        '-c:v', 'libx264', '-crf', '28', '-preset', 'veryfast',
        '-b:v', '500k',
        teaser_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        logger.error(f"❌ Error generating teaser: {result.stderr.decode('utf-8')}")
        raise Exception(f"FFmpeg failed: {result.stderr.decode('utf-8')}")

    return os.path.join('teasers', f'{video_id}_teaser.mp4')
