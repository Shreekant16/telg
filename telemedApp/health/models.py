from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=20)
    taluka = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)


class Doctor_Auth(models.Model):
    name = models.CharField(max_length=20)
    reg_no = models.CharField(max_length=20)


class AshaWorker_Auth(models.Model):
    name = models.CharField(max_length=20)
    id_no = models.CharField(max_length=20)


