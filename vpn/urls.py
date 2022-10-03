from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('newsletter/', views.news_letter_view, name='newsletter'),
    path('contact-form', views.contact_view, name='contact-form'),
    path('logout/', views.logoutUser, name='logout'),
    path('pricing/', views.pricing, name='pricing'),
    path('sign-in/', views.signin, name='sign-in'),
    path('sign-up/', views.signup, name='sign-up'),
    path('dashboard/', views.profile_management, name='dashboard'),
    path('checkout-page/<str:pk>', views.checkout, name='checkout-page'),
    path('create-checkout-session', views.CreateCheckoutSession.as_view(), name='create-checkout-session'),
    path('payment-success/', views.payment_succes, name='payement-success'),
    path('payment-cancel/', views.payment_cancel, name='payement-cancel'),
    path('webhook/stripe', views.my_webhook_view, name="webhook-stripe"),
    path('chart/filter-options/', views.get_filter_options, name='chart-filter-options'),
    path('chart/sales/<int:year>/', views.get_sales_chart, name='chart-sales'),
    path('chart/spend-per-customer/<int:year>/', views.spend_per_customer_chart, name='chart-spend-per-customer'),
    path('chart/payment-success/<int:year>/', views.payment_success_chart, name='chart-payment-success'),
]