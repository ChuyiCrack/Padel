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
   path('edit_profile/',views.edit_profile, name='edit'),
   path('match/<int:pk>',views.match,name='match'),
   path('history_matches/',views.history_matches,name='history_matches'),
   path('search_match/',views.search_match,name='search_match'),
   path('join_match/<int:pk>',views.join_match,name='join'),
   path('results/<int:pk>',views.submit_result,name='submit_result'),
   path('notifications/',views.notifications,name='notifications')
]