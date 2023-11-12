from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email field is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="custom_user_set",
        related_query_name="user",
        db_table='user_groups',
    )
    permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='user',
        db_table='user_permissions',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'user'

    def __str__(self):
        return f'<{self.__class__.__name__}>: {self.email}'

    def __repr__(self):
        return self.__str__()


class Payment(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="User",
        related_name="payments"
    )

    subscription = models.ForeignKey(
        'Subscription',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Subscription",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Amount Paid",
    )
    status = models.CharField(
        max_length=50,
        verbose_name="Payment Status",
        choices=(
            ('completed', 'Completed'),
            ('pending', 'Pending'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ),
        default='completed',
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Payment Date",
    )

    def __str__(self):
        return f'<{self.__class__.__name__}>: {self.user}-{self.subscription}-{self.date}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        db_table = 'user_payment'
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-date']


class Subscription(models.Model):

    title = models.CharField(max_length=10, verbose_name="Subscription Level")
    description = models.TextField(verbose_name="Description")
    ads_period_min = models.PositiveSmallIntegerField(verbose_name="Min ads period")
    ads_period_max = models.PositiveSmallIntegerField(verbose_name="Max ads period")
    managers_per_day = models.PositiveIntegerField(verbose_name="Managers per day")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    is_active = models.BooleanField(default=0)

    class Meta:
        db_table = 'subscription'
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        ordering = ['-price']


