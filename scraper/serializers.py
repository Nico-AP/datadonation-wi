from rest_framework import serializers

from scraper.models import TikTokVideo


class TikTokVideoSerializer(serializers.ModelSerializer):
    """ Serializer for TikTokVideo model. """
    username = serializers.StringRelatedField()
    hashtags = serializers.SlugRelatedField(
        many=True, slug_field='name', read_only=True
    )

    class Meta:
        model = TikTokVideo
        fields = '__all__'
