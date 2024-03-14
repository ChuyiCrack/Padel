from . import views
from django.urls import path

urlpatterns =[
   path('',views.index, name='index'),
   path('home/',views.home, name='home'),
   path('register',views.register,name='register'),
   path('logout/',views.logout_user, name='logout'),
   path('regions/',views.regions, name='regions'),
   path('courts/<int:pk>',views.courts, name='courts'),
   path('matching/<int:pk>',views.Matching, name='matching'),
   path('profile/<int:pk>',views.profile, name='profile'),
   path('match/<int:pk>',views.match,name='match'),
   path('history_matches/',views.history_matches,name='history_matches'),
   path('search_match/',views.search_match,name='search_match'),
   path('join_match/<int:pk>',views.join_match,name='join'),
   path('results/<int:pk>',views.submit_result,name='submit_result'),
   path('notifications_friend/',views.notifications_friends,name='notifications_friends'),
   path('invite_party/',views.invite_party,name='party'),
   path('notifications_party/',views.notifications_party,name='notifications_party'),
   path('change_profilepicture/',views.edit_profile_picture, name='profile_picture'),
   path('edit_bakground/',views.edit_background,name='background'),
   path('search_friends/',views.search_friends, name='search_friends'),
   path('match_information/<int:pk>',views.match_information, name= 'match_information'),
]