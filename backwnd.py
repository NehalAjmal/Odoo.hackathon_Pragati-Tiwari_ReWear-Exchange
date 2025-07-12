


backend:

models.py 
from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    size = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)  # For admin approval
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.title

class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='item_images/')
    is_primary = models.BooleanField(default=False)

class ItemTag(models.Model):
    item = models.ForeignKey(Item, related_name='tags', on_delete=models.CASCADE)
    tag = models.CharField(max_length=50)


serializer.py

from rest_framework import serializers
from .models import Item, ItemImage, ItemTag

class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ['id', 'image', 'is_primary']

    def validate_image(self, image):
        if image.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image size should be under 5MB.")
        if not image.content_type.startswith("image/"):
            raise serializers.ValidationError("Invalid image type.")
        return image

class ItemTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemTag
        fields = ['tag']

class ItemSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, write_only=True, required=False)
    tags = serializers.ListField(child=serializers.CharField(max_length=50), write_only=True, required=False)

    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'size', 'is_available', 'created_at', 'images', 'tags']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        tags_data = validated_data.pop('tags', [])
        item = Item.objects.create(user=self.context['request'].user, **validated_data)

        for image_data in images_data:
            ItemImage.objects.create(item=item, **image_data)

        for tag in tags_data:
            ItemTag.objects.create(item=item, tag=tag)

        return item

views.py
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Item
from .serializers import ItemSerializer

class ItemCreateListView(generics.ListCreateAPIView):
    queryset = Item.objects.filter(is_approved=True, is_available=True)
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.method in ['PUT', 'DELETE'] and obj.user != self.request.user:
            raise PermissionDenied("You do not own this item.")
        return obj

url.py
from django.urls import path
from .views import ItemCreateListView, ItemDetailView

urlpatterns = [
    path('api/items/', ItemCreateListView.as_view(), name='item-list-create'),
    path('api/items/<int:pk>/', ItemDetailView.as_view(), name='item-detail'),
]

settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


project/urls.py
Serve media files in development:

python
Copy
Edit
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # your other urls...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT