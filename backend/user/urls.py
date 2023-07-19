from django.urls import path
from . import views

'''

注意命名驼峰
比如userInfo 不是 userinfo

比如 getTruePrivacy 不是 gettrueprivacy
'''
urlpatterns = [
    path('account/', views.account, name='account'),
    path('state/', views.state, name='state'),
    path('verify/', views.verify, name='verify'),
    path('userinfo/', views.UserInfo, name='userinfo'),
    path('privacyinfo/', views.PrivacyInfo, name='privacyinfo'),
    path('gettrueprivacy/', views.getTruePrivacy, name='gettrueprivacy'),
    path('browseinfo/', views.BrowseInfo, name='browseinfo'),
    path('collectedinfo/', views.CollectedInfo, name='collectedinfo'),
    path('getmessagelist/', views.getMessageList, name='getmessagelist')
]