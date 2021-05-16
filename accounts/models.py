import random

from django.db import models
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.template import loader
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.base_user import BaseUserManager
from making_jods.models import BaseModel
from making_jods import settings
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other')
)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=32, null=True)
    is_accepted_tc = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    account_activation_token = models.CharField(max_length=255, null=True, blank=True)
    is_email_verify = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.get_full_name

    @property
    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = f'{self.first_name} {self.last_name}'
        return full_name

    @property
    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self):
        """
        Send an email to User.
        """
        otp = random.randrange(1000, 9999, 4)
        template = loader.get_template('email_verification.html')
        email_body = template.render({
            'otp': otp
        })
        email = EmailMessage(
            "Email Verification Making Jods",
            body=email_body,
            from_email=settings.FROM_EMAIL,
            to=[self.email])
        email.content_subtype = "html"
        email.send()
        self. account_activation_token = otp
        self.save()


class Profile(BaseModel):
    user = models.OneToOneField("accounts.User", related_name="profile_user", blank=False,
                                null=False, on_delete=models.CASCADE,
                                db_index=True)
    profile_photo = models.FileField(upload_to="profile_pics", null=True, blank=True)
    show_name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    interest = models.ManyToManyField('accounts.Interest', blank=True, related_name='profile_interest')
    profile_visitor = models.ManyToManyField('accounts.User', blank=True, related_name='profile_visitor')
    point_badge = models.ForeignKey('accounts.PointsCategory', blank=True, null=True, on_delete=models.CASCADE,
                                    related_name='badge')

    def __str__(self):
        return self.user.get_full_name


class Interest(BaseModel):
    name = models.CharField(max_length=50)
    sub_interest = models.ForeignKey('accounts.Interest', on_delete=models.CASCADE,
                                     null=True, related_name='interest_sub')

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Points(BaseModel):
    activity_name = models.CharField(max_length=255)
    points = models.IntegerField()

    def __str__(self):
        return self.activity_name

    @property
    def slug_name(self):
        return self.activity_name.lower().replace(' ', '_')


class PointsCategory(BaseModel):
    points_category = models.CharField(max_length=255)
    points = models.IntegerField()

    def __str__(self):
        return self.points_category


class ActivityPoints(BaseModel):
    activity_name = models.CharField(max_length=255)
    points = models.IntegerField()
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='user_activity')

    def __str__(self):
        return self.user.first_name


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'),
                                                   reset_password_token.key)
    send_mail(
        # title:
        "Password Reset for {title}".format(title="Making Jods"),
        # message:
        email_plaintext_message,
        # from:
        "devtestmakingjods@gmail.com",
        # to:
        [reset_password_token.user.email]
    )
