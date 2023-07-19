from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('valid/', views.valid, name='valid'),
    path('verify/', views.verify, name='verify'),
    path('userinfo/', views.UserInfo, name='userinfo'),
    path('privacyinfo/', views.PrivacyInfo, name='privacyinfo'),
    path('gettrueprivacy/', views.getTruePrivacy, name='gettrueprivacy'),
    path('browseinfo/', views.BrowseInfo, name='browseinfo'),
    path('collectedinfo/', views.CollectedInfo, name='collectedinfo'),
    path('getmessagelist/', views.getMessageList, name='getmessagelist')
]