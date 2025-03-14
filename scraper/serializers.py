from rest_framework import serializers

from scraper.models import TikTokVideo, TikTokVideo_B


class TikTokVideoSerializer(serializers.ModelSerializer):
    """ Serializer for TikTokVideo model. """
    username = serializers.StringRelatedField()
    hashtags = serializers.SlugRelatedField(
        many=True, slug_field='name', read_only=True
    )

    class Meta:
        model = TikTokVideo
        fields = '__all__'


class TikTokVideoBSerializer(serializers.ModelSerializer):
    author_id = serializers.StringRelatedField()
    author_username = serializers.CharField(source='author_id.username', read_only=True)
    hashtags = serializers.SlugRelatedField(
        many=True, slug_field='name', read_only=True
    )

    class Meta:
        model = TikTokVideo_B
        fields = [
            field.name for field in TikTokVideo_B._meta.get_fields()
        ]
        fields += ['author_username']
