from django.contrib import admin

# Register your models here.
from .models import LogFileProcessor
admin.site.register({LogFileProcessor})