from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from videos.models import Video, VideoProgress

User = get_user_model()

class VideoAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.video = Video.objects.create(
            title='Test Video',
            slug='test-video',
            video_file='videos/test.mp4',
            status='Done'
        )

    def test_video_list(self):
        response = self.client.get('/api/videos/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['slug'], self.video.slug)

    def test_video_detail(self):
        response = self.client.get(f'/api/videos/{self.video.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], self.video.title)

    def test_video_progress_save_and_get(self):
        # Login required
        self.client.login(username='testuser', password='testpass')
        progress_url = f'/api/videos/{self.video.slug}/progress/'

        # POST progress
        response = self.client.post(progress_url, {
            "progress": 42.5,
            "seen": True
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(VideoProgress.objects.filter(user=self.user, video=self.video).exists())

        # GET progress
        response = self.client.get(progress_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['progress'], 42.5)
