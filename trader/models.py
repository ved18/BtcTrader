from django.db import models

# Create your models here.
class Client(models.Model):
    id = models.IntegerField(db_column='id', primary_key=True)
    firstname = models.CharField(db_column='firstName', max_length=255)  # Field name made lowercase.
    lastname = models.CharField(db_column='lastName', max_length=255)  # Field name made lowercase.
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255, blank=True, null=True)
    zip = models.IntegerField()
    phonenumber = models.IntegerField(db_column='phoneNumber')  # Field name made lowercase.
    cellnumber = models.IntegerField(db_column='cellNumber', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'client'