from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("relation/", views.RelationQuery, name="RelationQuery"),
    path("query", views.queryEntity, name="entityQuery"),
    path("cut", views.cut_sentence, name='cut_sentence'),
    path("intelligentQuery", views.IntelligentQuery, name="intelligentQuery"),
    path("recommendation",views.recommendation,name="recommendation"),
    path("getProYearsInfo/", views.getProYearsInfo, name="getProYearsInfo"),
    path("getCateDegreeInfo/",
         views.getCateDegreeInfo,
         name="getCateDegreeInfo"),
    path("getScoreInfo/", views.getScoreInfo, name="getScoreInfo"),
    path("scoreRecommend/", views.ScoreRecommend, name="ScoreRecommend")
]
