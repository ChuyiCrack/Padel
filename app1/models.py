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
    last_activity=models.DateTimeField(default=timezone.now,blank=True)
    party=models.ManyToManyField('self', symmetrical=True,blank=True)

    def add_party(self,friend):
        if ((self.party.count())<2):
            self.party.add(friend)
            self.save()
        return 


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
    ranked=models.BooleanField()

    def __str__(self):
        return f'{self.Creator.owner.username} -- {self.id}'
    
class result(models.Model):
    target_match=models.ForeignKey(Match,on_delete=models.CASCADE,related_name='match')
    winner=models.ForeignKey(Account,blank=True,on_delete=models.SET_NULL,null=True,related_name='won_matches')
    looser=models.ForeignKey(Account,blank=True,on_delete=models.SET_NULL,null=True,related_name='losed_matches')
    res_creator=models.CharField(max_length=15,default='NONE',blank=True)
    res_joined=models.CharField(max_length=15,default='NONE',blank=True)
    creator_score=models.PositiveIntegerField(blank=True, default=0)
    joined_score=models.PositiveIntegerField(blank=True, default=0)
    submited=models.BooleanField(default=False)

    def __str__(self):
        return f'REsult of the match {self.target_match.id}'
    
class friend_requests(models.Model):
    sender=models.ForeignKey(Account,on_delete=models.CASCADE,related_name='sender_request')
    receiver=models.ForeignKey(Account,on_delete=models.CASCADE,related_name='receiver_request')
    data=models.DateTimeField(default=timezone.now)
    checked=models.BooleanField(default=False)

    def __str__(self):
        return f'From {self.sender} to {self.receiver}'

class notification(models.Model):
    type=models.CharField(max_length=20)
    message=models.TextField(max_length=50)

class friend_notification(notification):
    friend_to_add=models.ForeignKey(friend_requests,on_delete=models.CASCADE,related_name='friend_request')