from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("relation/", views.RelationQuery, name="RelationQuery"),
    path("query", views.queryEntity, name="entityQuery"),
    path("cut", views.cut_sentence, name='cut_sentence')
]
