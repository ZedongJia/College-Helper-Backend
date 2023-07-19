from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
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
=======
    path('account/', views.account, name='account'),
    path('state/', views.state, name='state'),
    path('verify/', views.verify, name='verify')
>>>>>>> b4bc378868ecf169416048d4ec9565bbc69d66f9
]