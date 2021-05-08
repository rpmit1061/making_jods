from rest_framework import serializers
from posts import models as post_model


class CommentsSerializer(serializers.ModelSerializer):
    user = serializers.CharField(required=False)

    class Meta:
        model = post_model.Comments
        fields = ['comment', 'user']


class PostSerializer(serializers.ModelSerializer):
    comments = CommentsSerializer(many=True)

    class Meta:
        model = post_model.Posts
        fields = '__all__'



