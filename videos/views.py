from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from .models import VideoProgress, Video  
from .serializers import VideoSerializer

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class VideosView(generics.ListCreateAPIView):
    """
    API-View für die Liste & Erstellung von Videos.
    Nur authentifizierte Nutzer können diese API nutzen.
    """
    permission_classes = [AllowAny]
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class VideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API-View für einzelne Videos (Abrufen, Aktualisieren, Löschen).
    Lookup erfolgt über `slug`.
    """
    permission_classes = [AllowAny]
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    lookup_field = 'slug'

class VideoProgressView(APIView):
    """
    API-View für das Speichern & Abrufen des Wiedergabefortschritts eines Videos.
    """
    permission_classes = [AllowAny]

    def get(self, request, video_slug):
        """
        Holt den Fortschritt des eingeloggten Nutzers für ein bestimmtes Video.
        """
        video = get_object_or_404(Video, slug=video_slug)        
        progress_record = VideoProgress.objects.filter(user=request.user, video=video).first()
        progress = progress_record.progress if progress_record else 0.0
        return Response({"progress": progress})

    def post(self, request, video_slug):
        """
        Speichert oder aktualisiert den Wiedergabefortschritt eines Videos.
        """
        video = get_object_or_404(Video, slug=video_slug)

        try:
            progress = float(request.data.get("progress", 0.0))
        except ValueError:
            return Response({"error": "Invalid progress value"}, status=400)

        seen = request.data.get("seen", False)

        progress_record, created = VideoProgress.objects.get_or_create(user=request.user, video=video)
        progress_record.progress = progress
        progress_record.seen = seen 
        progress_record.save()
        
        return Response({"message": "Progress saved successfully"})
