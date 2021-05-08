from django.urls import path, include
from rest_framework import routers
from posts import views
router = routers.SimpleRouter()
router.register('', views.PostViewSet)
# router.register('comments', views.CommentsViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('comments/<int:post_id>/', views.CommentsViewSet.as_view({'post': 'create'}))
]