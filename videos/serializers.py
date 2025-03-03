from rest_framework import serializers
from .models import Video, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']  

class VideoSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True,required=False ) 
    video_file = serializers.FileField(required=False)
    teaser_file = serializers.FileField(required=False)
    thumbnail = serializers.ImageField(required=False)
    slug = serializers.SlugField(read_only=True)  

    class Meta:
        model = Video
        fields = '__all__'


