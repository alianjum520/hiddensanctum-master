from django.urls import path
from .views import SignUpUser, UserData

urlpatterns = [
    path('sign-up/', SignUpUser.as_view()),
    path('user-data/', UserData.as_view()),
]