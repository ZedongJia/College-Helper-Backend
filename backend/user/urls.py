from django.urls import path
from . import views

'''

注意命名驼峰
比如userInfo 不是 userinfo

比如 getTruePrivacy 不是 gettrueprivacy
'''
urlpatterns = [
    path('account/', views.account, name='account'),
    path('quick/', views.quick, name='quick'),
    path('code/', views.getcode, name='code'),
    path('modifyPW/', views.updatePW, name='modifyPW'),
    path('state/', views.state, name='state'),
    path('userInfo/', views.userInfo, name='userInfo'),
    path('privacyInfo/', views.privacyInfo, name='privacyInfo'),
    path('getOpenInfo/', views.getOpenInfo, name='getOpenInfo'),
    path('getBrowseInfo/', views.getBrowseInfo, name='getBrowseInfo'),
    path('getCollectionInfo/', views.getCollectionInfo, name='getCollectionInfo'),
    # path('getmessagelist/', views.getMessageList, name='getmessagelist')
]
