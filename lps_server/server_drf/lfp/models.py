import uuid
from datetime import datetime
from django.db import models
#from postgres_copy import CopyManager

# Create your models here.
class LogFileProcessor(models.Model):

    
    # PK
    logdetail_id = models.UUIDField(verbose_name="did",primary_key=True, default=uuid.uuid4, editable=False) 
    log_line = models.CharField(max_length=1000, null=True, blank=True)
    
    # Filters
    fyear = models.CharField(max_length=4, null=True, blank=True)
    fmonth = models.CharField(max_length=2, null=True, blank=True)
    fday = models.CharField(max_length=2, null=True, blank=True)
    
    fhour = models.CharField(max_length=2, null=True, blank=True)
    fminute = models.CharField(max_length=2, null=True, blank=True)
    fsecond = models.CharField(max_length=2, null=True, blank=True)
    
    fdate = models.CharField(max_length=8, null=True, blank=True)
    ftime = models.CharField(max_length=6, null=True, blank=True)    
    fdatetime = models.CharField(max_length=14, null=True, blank=True)    
    
    frequest = models.CharField(max_length=500, null=True, blank=True)
    fip = models.CharField(max_length=40, null=True, blank=True)
    freferer = models.CharField(max_length=500, null=True, blank=True)
    fuser_agent = models.CharField(max_length=500, null=True, blank=True)
    fstatus = models.CharField(max_length=10, null=True, blank=True)
    ftime_taken = models.BigIntegerField(default=0)
    
    fbyte = models.IntegerField(default=0)
    fextension = models.CharField(max_length=10, null=True, blank=True)
    
    # Reservation Fields
    freserve1 = models.CharField(max_length=500, null=True, blank=True)
    freserve2 = models.CharField(max_length=500, null=True, blank=True)
    freserve3 = models.CharField(max_length=500, null=True, blank=True)
    
    created = models.DateTimeField(auto_now=True, verbose_name="date create")   
    
    # For Mass Insert Logs
    #objects = CopyManager()
    
    def __str__(self):
        return str(self.project_id)

    class Meta:
        ordering = ['created']