from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from vpn.api.utils import Util
from datetime import date



# Create your models here.
User._meta.get_field('email')._unique = True

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

	def Amount(self):
		return self.plans__price


class Membership(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
	plans = models.ForeignKey(Plan, on_delete=models.CASCADE, null=True, blank=True)
	sluged = models.CharField(max_length=1000)
	premium_membership = models.BooleanField(default=False)
	payment_completed = models.BooleanField(default=False)
	cancel_membership = models.BooleanField(default=False)
	subscription_date = models.DateField(null=True, blank=True)
	expiration_data = models.DateField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

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


class EmailToken(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	token = models.CharField(max_length=555)
	expired  = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	expiration_time = models.DateTimeField(blank = True, null=True)


	def __str__(self):
		return self.token


class Blog(models.Model):
	title = models.CharField(max_length=300)
	slug = models.SlugField(max_length=300)
	image = models.ImageField(upload_to='blog_images/')
	content = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return self.title
	def image_tag(self):
		from django.utils.html import mark_safe
		return mark_safe('<img src="{}" width="60" height="70" />'.format(self.image.url))
	image_tag.short_description = 'Image'


class Contact(models.Model):
    name = models.CharField( max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name



#signals created for updatinf model and sending mails
@receiver(post_save, sender=Membership)
def MembershipUpdate(sender, created, instance, **kwargs):
	print(date.today())
	if instance.expiration_data == date.today():
		instance.premium_membership = False
		if instance.payment_completed == True:
			instance.payment_completed = False
			instance.save()


@receiver(post_save, sender=Membership)
def MembershipExpiration(sender, created, instance, **kwargs):

	membership = Membership.objects.filter(premium_membership = False)
	for expired_membership in membership:

		email_body = 'Hi '+expired_membership.user.username + \
					'Your Membership has been expired or Please Pay your Membership chargers to use premium services \n'

		data = {'email_body': email_body, 'to_email': expired_membership.user.email,
				'email_subject': 'Pay your Membership chargers'}
		Util.send_email(data)

