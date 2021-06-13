from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from making_jods.utils import CustomResponse
from posts import models as post_models
from posts import serializer as post_serializer
# Create your views here.
from posts.utils import add_points


class PostViewSet(viewsets.ModelViewSet):
    queryset = post_models.Posts.objects.all()
    serializer_class = post_serializer.PostSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post']
    renderer_classes = [CustomResponse]


class CommentsViewSet(viewsets.ModelViewSet):
    queryset = post_models.Comments.objects.all()
    serializer_class = post_serializer.CommentsSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post']
    renderer_classes = [CustomResponse]

    def create(self, request, post_id, *args, **kwargs):
        user = request.user
        post = post_models.Posts.objects.get(id=post_id)
        comments = post.comments.create(user=user, comment=request.data.get('comment', ''))
        if comments:
            add_points(post.user, activity_name="Comments")
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Comment done on post',
            }
            return Response(response)
        return Response({"detail": "Something went wrong please try again."}, status=status.HTTP_400_BAD_REQUEST)
