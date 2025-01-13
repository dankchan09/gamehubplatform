from django.db import models

# Create your models here.
class Game(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    release_date = models.DateField()  

class Member(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    date_register = models.DateTimeField(null=True)
    password = models.CharField(max_length=100)
    
    def __str__(self):
        return self.first_name + " " + self.last_name

class Profile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    bio = models.TextField()  
