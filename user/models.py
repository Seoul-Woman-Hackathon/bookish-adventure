from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.gis.db import models
from map_alarm.models import Accidents


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    iduser = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    birthdate = models.DateField()
    phonenum = models.CharField(max_length=100)
    pic = models.ImageField(blank=True, null=True, upload_to="profile_pics/")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    count = models.IntegerField(default=1)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "birthdate", "phonenum"]

    class Meta:
        db_table = "User"


class UserHasAccidents(models.Model):
    user_iduser = models.ForeignKey(User, models.CASCADE, db_column="user_iduser")
    accidents_idaccidents = models.ForeignKey(
        Accidents, models.CASCADE, db_column="accidents_idaccidents"
    )

    class Meta:
        managed = False
        db_table = "user_has_accidents"
        unique_together = (("user_iduser", "accidents_idaccidents"),)
