from django.contrib import admin

from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(BloodGroup)
admin.site.register(RhesusFactor)
admin.site.register(Request)
admin.site.register(Location)