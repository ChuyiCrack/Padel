from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Region(models.Model):
    Name=models.CharField(max_length=40)
    image=models.ImageField(upload_to='./regions',blank=True)

    def __str__(self):
        return self.Name
    
class Courts(models.Model):
    Name=models.CharField(max_length=40)
    region=models.ForeignKey(Region,on_delete=models.CASCADE)
    Location=models.TextField(max_length=100,blank=True)
    image=models.ImageField(upload_to='./images',blank=True)

    lat=models.CharField(max_length=40,blank=True,null=True)
    lng=models.CharField(max_length=40,blank=True,null=True)
    place_id=models.CharField(max_length=40,blank=True,null=True)

    def __str__(self):
        return self.Name
    

class Account(models.Model):
    owner=models.ForeignKey(User,on_delete=models.CASCADE)
    profile_picture=models.ImageField(upload_to='./profile_picture',blank=True,default='./profile_picture/default.jpg')
    homepage_picture=models.ImageField(upload_to='./profile_picture',blank=True,default='./profile_picture/default_homepage.jpg')
    points=models.IntegerField(default=500)
    played_matches=models.PositiveIntegerField(default=0)
    wins=models.PositiveIntegerField(default=0)
    friends=models.ManyToManyField('self', symmetrical=True,blank=True)

    def calculate_winrate(self):
        if self.played_matches==0:
            return 0
        return (self.wins/self.played_matches)*100
    
    def __str__(self):
        return self.owner.username
    
class Match(models.Model):
    Creator=models.ForeignKey(Account,on_delete=models.SET_NULL,null=True,related_name='creator_match')
    Active=models.BooleanField(default=True)
    started=models.BooleanField(default=False)
    Joined=models.ForeignKey(Account,blank=True,on_delete=models.SET_NULL,null=True,related_name='oponent_match')
    court=models.ForeignKey(Courts,blank=False,on_delete=models.SET_NULL,null=True,related_name='court_match')
    date_created=models.DateTimeField(default=timezone.now)
    Winner=models.ForeignKey(Account,blank=True,on_delete=models.SET_NULL,null=True,related_name='won_matches')
    Looser=models.ForeignKey(Account,blank=True,on_delete=models.SET_NULL,null=True,related_name='losed_matches')

    def __str__(self):
        return f'{self.Creator.owner.username} -- {self.id}'

