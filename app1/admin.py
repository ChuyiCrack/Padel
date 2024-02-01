from django.contrib import admin
from .models import Region,Courts,Account,Match,result,friend_requests

admin.site.register(Region)
admin.site.register(Courts)
admin.site.register(Account)
admin.site.register(Match)
admin.site.register(result)
admin.site.register(friend_requests)
