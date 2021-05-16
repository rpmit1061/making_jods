from django.urls import path, include
from rest_framework import routers
from accounts import views
router = routers.SimpleRouter()
router.register('user', views.UserViewSet)
router.register('registration', views.UserRegistrationViewSet)
router.register('profile', views.ProfileViewSet)
router.register('interest', views.InterestViewSet)


urlpatterns = router.urls

urlpatterns += [
    path('login', views.LoginViewSet.as_view({'post': 'login'})),
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    # path('auth/google', views.GoogleLogin.as_view(), name='google_login'),
]
