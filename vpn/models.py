from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Plan(models.Model):
	title = models.CharField(max_length=50, blank=False, null=False)
	price = models.IntegerField(default=0, null=True, blank=True)
	plan_duration_months  = models.IntegerField(default=1,
                                     null=True,
                                     blank=True,
                                     validators=[MaxValueValidator(12), MinValueValidator(1)])
	plan_duration_title = models.CharField(max_length=50, blank=False, null=False, default= "Free ")
	feature_one = models.CharField(max_length=100, null=True, blank=True)
	feature_two = models.CharField(max_length=100, null=True, blank=True)
	feature_three = models.CharField(max_length=100, null=True, blank=True)
	feature_four = models.CharField(max_length=100, null=True, blank=True)



	def __str__(self):
		return self.title


class Membership(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
	plans = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True)
	sluged = models.CharField(max_length=1000)
	premium_membership = models.BooleanField(default=False)
	payment_completed = models.BooleanField(default=False)
	cancel_membership = models.BooleanField(default=False)
	subscription_date = models.DateField(null=True, blank=True)
	expiration_data = models.DateField(null=True, blank=True)

	def __str__(self):
		return self.user.username
	def slug(self):
		return slugify("{self.plans.title} {self.id}".format(self=self))


class Server(models.Model):
	server_name = models.CharField(max_length=100, blank=False, null=False)
	region = models.CharField(max_length=10, blank=False, null=False)
	hostname = models.CharField(max_length=100, blank=False, null=False)
	server_username = models.CharField(max_length=100)
	server_password = models.CharField(max_length=100)
	flag_code = models.CharField(max_length=50, blank=False, null=False)
	premium_server = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.server_name


class NewsLetter(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email