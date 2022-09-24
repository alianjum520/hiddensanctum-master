from django.urls import path
from .views import (
    SignUpUser,
    LoginView,
    LogOutView,
    ServerView,
    ServerPostView
    )

urlpatterns = [
    path('sign-up/', SignUpUser.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogOutView.as_view()),
    path('server/', ServerView.as_view()),
    path('server-post/', ServerPostView.as_view())
]