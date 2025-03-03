from datetime import date
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Kategorienamen einzigartig machen

    def __str__(self):
        return self.name
   

class Video(models.Model):
    title = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100, unique=True, blank=False)
    description = models.TextField(max_length=500)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    teaser_file = models.FileField(upload_to='teasers/', blank=True, null=True)
    hls_playlist = models.FileField(upload_to='hls_playlists/', blank=True, null=True)
    thumbnail = models.FileField(upload_to='thumbnails/', blank=True, null=True)
    created_at = models.DateField(default=date.today)
    categories = models.ManyToManyField(Category, related_name='videos')
    status = models.CharField(max_length=20, default='pending')  # FREI WÄHLBAR, kein Choices-Feld

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Video.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class VideoProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    progress = models.FloatField(
        default=0.0, 
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    seen = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'video')  # Jeder User kann nur EINEN Wiedergabefortschritt pro Video haben

    def __str__(self):
        return f"{self.video.title} - {self.user.username} ({self.progress}%)"

