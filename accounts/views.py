from django.contrib.auth import authenticate
from django.db.models import Sum

from rest_framework.response import Response
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken

# from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
# from allauth.socialaccount.providers.oauth2.client import OAuth2Client
# from rest_auth.registration.views import SocialLoginView

from accounts import models as account_models
from accounts import serializer as account_serializer
from making_jods.utils import CustomResponse
from posts.utils import add_points


class UserViewSet(viewsets.ModelViewSet):
    """ get API's for the getting users list and user details. """
    queryset = account_models.User.objects.all()
    serializer_class = account_serializer.UserSerializer
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomResponse]


    def get_serializer_class(self):
        if self.action == 'change_password':
            return account_serializer.ChangePasswordSerializer
        return account_serializer.UserSerializer

    @action(detail=True, methods=['post'])
    def change_password(self, request, *args, **kwargs):
        user_object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not user_object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            user_object.set_password(serializer.data.get("new_password"))
            user_object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistrationViewSet(viewsets.ModelViewSet):
    """ This is the API for the User registration."""
    queryset = account_models.User.objects.all()
    serializer_class = account_serializer.UserRegistrationSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post', 'patch']
    renderer_classes = [CustomResponse]

    def create(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request.data)
        if ser.is_valid(raise_exception=True):
            obj = ser.save()
            obj.set_password(obj.password)
            obj.save()
            obj.email_user()
        return Response({'details': "User Created Successfully."}, status=status.HTTP_200_OK)


class LoginViewSet(viewsets.ModelViewSet):
    queryset = account_models.User.objects.none()
    serializer_class = account_serializer.LoginSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post']
    renderer_classes = [CustomResponse]


    @action(detail=False, methods=['post'])
    def login(self, request, **kwargs):
        email = request.data['email']
        password = request.data['password']
        otp = request.data.get('otp', '')

        user = authenticate(username=email, password=password)
        if not user:
            return Response({'detail': "Email And Password not Matched."})
        else:
            if user.is_email_verify and user.account_activation_token is not None:
                token = RefreshToken.for_user(user)
                response = {
                    'username': user.first_name,
                    'access_token': str(token.access_token),
                    'refresh_token': str(token)
                }
                return Response(response)
            elif otp:
                if otp == int(user.account_activation_token):
                    user.is_email_verify = True
                    user.account_activation_token = None
                    user.save()
                    add_points(user, activity_name="Sign Up")
                    return Response({'detail': "Email Verify successfully."}, status=status.HTTP_200_OK)
                return Response({'detail': "OTP is Invalid."}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                user.email_user()
                return Response({"detail": "Your Email is not verify. Please check and verify Email."})


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = account_models.Profile.objects.all()
    serializer_class = account_serializer.ProfileSerializer
    http_method_names = ['get', 'post']
    permission_classes = [AllowAny]
    renderer_classes = [CustomResponse]


    def retrieve(self, request, *args, **kwargs):
        visitor_user= self.request.user
        profile_user = self.get_object()
        if visitor_user is not profile_user and not profile_user.profile_visitor.filter(id=visitor_user.id).exists():
            profile_user.profile_visitor.add(visitor_user)
            add_points(user=profile_user.user, activity_name="Profile Watch")

        return super(ProfileViewSet, self).retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def get_points(self, request, *args, **kwargs):
        points = self.get_object().user.user_activity.aggregate(total_points=Sum('points'))
        return Response(points)


class InterestViewSet(viewsets.ModelViewSet):
    queryset = account_models.Interest.objects.all()
    serializer_class = account_serializer.InterestSerializer
    http_method_names = ['get']
    permission_classes = [AllowAny]
    renderer_classes = [CustomResponse]

