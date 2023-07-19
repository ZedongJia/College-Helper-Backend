from django.urls import path
from . import views

urlpatterns = [
    path('account/', views.account, name='account'),
    path('state/', views.state, name='state'),
    path('verify/', views.verify, name='verify')
]