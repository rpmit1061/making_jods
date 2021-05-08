from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

# Create your models here.
from making_jods.models import BaseModel


class Comments(BaseModel):
    comment = models.TextField()
    user = models.ForeignKey('accounts.User',  on_delete=models.CASCADE, related_name='comment_user')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.comment


class Posts(BaseModel):
    user = models.ForeignKey('accounts.User',  on_delete=models.CASCADE, related_name='post_user')
    interest = models.ForeignKey('accounts.Interest', on_delete=models.CASCADE, related_name='post_interest')
    description = models.TextField()
    image = models.FileField(upload_to='post_images', null=True, blank=True)
    post_date = models.DateField(null=True, blank=True)
    post_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255)
    max_people = models.IntegerField(null=True)
    comments = GenericRelation(Comments, related_query_name='post_comments')

    def __str__(self):
        return self.description
