from django.urls import path
from .views import (
    SignUpUser,
    LoginView,
    LogOutView,
    ServerView,
    ServerPostView,
    ServerRetrieveView,
    VerifyEmail,
    RenewTokenView,
    ChangePasswordView,
    RequestPasswordResetEmail,
    SetNewPasswordAPIView
    )

urlpatterns = [
    path('sign-up/', SignUpUser.as_view(), name = 'sign-up'),
    path('renew-token/', RenewTokenView.as_view(), name = 'renew-token'),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('email-verify/<str:token>', VerifyEmail.as_view(), name="email-verify"),
    path('login/', LoginView.as_view()),
    path('logout/', LogOutView.as_view()),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('server/', ServerView.as_view()),
    path('server/<int:id>', ServerRetrieveView.as_view()),
    path('server-post/', ServerPostView.as_view()),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(),
         name="request-reset-email"),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(),
         name='password-reset-complete'),
    path('password-reset-complete/<str:token>', SetNewPasswordAPIView.as_view(),
         name='password-reset-complete')
]