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
	#plan_duration_title = models.CharField(max_length=50, blank=False, null=False, default= "Free ")
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
	premium = models.BooleanField(default=False)
	payment_completed = models.BooleanField(default=False)
	cancel_membership = models.BooleanField(default=False)
	subscription_date = models.DateField(null=True, blank=True)
	expiration_data = models.DateField(null=True, blank=True)

	def __str__(self):
		return self.user.username
	def slug(self):
		return slugify(f"{self.plans.title} {self.id}")
