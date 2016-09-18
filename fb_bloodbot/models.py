from __future__ import unicode_literals

from django.db import models

# Create your models here.
class User(models.Model):
	name = models.CharField(max_length=200)
	gender = models.CharField(max_length=20, null=True)
	fbId = models.CharField(max_length=200, primary_key=True, unique=True)
	bloodGroup = models.ForeignKey('BloodGroup', on_delete=models.CASCADE)
	rhesusFactor = models.ForeignKey('RhesusFactor', on_delete=models.CASCADE)
	status = models.CharField(max_length=200)
	last_donation = models.DateField(null=True)

	def __str__(self):
		return self.name


class Request(models.Model):
	recipient = models.ForeignKey('User', on_delete=models.CASCADE)
	location = models.ForeignKey('Location', on_delete=models.CASCADE, null=True)
	bloodGroup = models.ForeignKey('BloodGroup', on_delete=models.CASCADE, null=True)
	rhesusFactor = models.ForeignKey('RhesusFactor', on_delete=models.CASCADE, null=True)
	status = models.CharField(max_length=200, null=True)
	recipient_ph_no = models.CharField(max_length=10)

class BloodGroup(models.Model):
	bloodGroup = models.CharField(max_length=5, null=True)

	def __str__(self):
		return self.bloodGroup

class RhesusFactor(models.Model):
	RhFactor = models.NullBooleanField()

	def __str__(self):
		if self.RhFactor:
			return "Positive"
		else:
			return "Negative"

class Location(models.Model):
	lat = models.FloatField(null=True)
	lon = models.FloatField(null=True)
	name = models.CharField(max_length=200,null=True)
	users = models.ManyToManyField('User')

	def __str__(self):
		return self.name