from django.urls import path
from .views import VideosView, VideoDetailView, VideoProgressView

urlpatterns = [
    path('videos/', VideosView.as_view(), name='video-list'),
    path('videos/<slug:slug>/', VideoDetailView.as_view(), name='video-detail'),
    path('videos/<slug:video_slug>/progress/', VideoProgressView.as_view(), name='video-progress'),
]
