from django.urls import path
from . import views

"""

注意命名驼峰
比如userInfo 不是 userinfo

比如 getTruePrivacy 不是 gettrueprivacy
"""
urlpatterns = [
    path("account", views.account, name="account"),
    path("quick", views.quick, name="quick"),
    path("code", views.getcode, name="code"),
    path("modifyPW", views.updatePW, name="modifyPW"),
    path("state", views.state, name="state"),
    path("userInfo", views.userInfo, name="userInfo"),
    path("privacyInfo", views.privacyInfo, name="privacyInfo"),
    path("getOpenInfo", views.getOpenInfo, name="getOpenInfo"),
    path("getBrowseInfo", views.getBrowseInfo, name="getBrowseInfo"),
    path("addBrowseInfo", views.addBrowseInfo, name="addBrowseInfo"),
    path("getCollectionInfo", views.getCollectionInfo, name="getCollectionInfo"),
    path("star", views.star, name="star"),
    path("getSession", views.getSession, name="getSession"),
    path("getMessageList", views.getMessageList, name="getMessageList"),
    path("addMessage", views.addMessage, name="addMessage"),
    path("dropSession", views.dropSession, name="dropSession"),
    path("getReview", views.getReview, name="getReview"),
    path("addReview", views.addReview, name="addReview"),
    path("removeReview", views.removeReview, name="removeReview"),
    path("queryFollow", views.queryFollow, name="queryFollow"),
    path("queryFollowList", views.queryFollowList, name="queryFollowList"),
    path("querySession", views.querySession, name="querySession"),
    path("queryFeedback", views.queryFeedback, name="queryFeedback"),
    path("follow", views.follow, name="follow"),
    path("addSession", views.addSession, name="addSession"),
    path("addFeedback", views.addFeedback, name="addFeedback"),
]
