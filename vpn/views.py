from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import Plan, Membership
from django.contrib.auth.models import User
import stripe
from django.conf import settings
from django.views.generic import View
import datetime
from dateutil.relativedelta import relativedelta

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

def index(request):
    return render(request, 'vpn/index.html')

def pricing(request):
    plans = Plan.objects.all()

    context = {
        'plans': plans
    }
    return render(request, 'vpn/pricing.html', context)

def signin(request):
    if request.user.is_authenticated:
        return redirect('pricing')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('pricing')
        else:
            messages.error(request, 'Username or Password is incorrect')
    return render(request, 'vpn/form.html')

def signup(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'Congratulations Registered Successfully..!')
            login(request, user)
            return redirect('pricing')

        else:
            messages.error(request, 'An error has occured during registration')
    context = {'form': form}
    return render(request, 'vpn/form.html', context)

def logoutUser(request):
    logout(request)
    messages.error(request, 'User was successfully logout')
    return redirect('sign-in')


def profile_management(request):
    user = request.user
    user_details = User.objects.get(username = user)
    membership = Membership.objects.get(user = user)
    context = {
        "user": user,
        "user_details": user_details,
        "membership": membership
    }
    return render(request, 'vpn/profile.html', context)


def checkout(request,pk):
    """This is the checkout page that will tell us which plan the user opt"""

    if request.user.is_authenticated:
        plans = Plan.objects.get(id=pk)
        if plans.price != 0:
            try:
                membership = Membership.objects.get(user = request.user)
                membership.plans = plans
                membership.save()
                context = {
                    'plans':plans,
                    'membership':membership
                }
                return render(request, 'vpn/checkout_view.html', context)

            except Membership.DoesNotExist:
                membership = Membership.objects.create(
                user = request.user,
                plans = plans
                )
                context = {
                    'plans':plans,
                    'membership':membership
                }
                return render(request, 'vpn/checkout_view.html', context)
        else:
            try:
                membership = Membership.objects.get(user = request.user)
                membership.plans = plans
                membership.save()
                return render(request,'vpn/profile.html')

            except Membership.DoesNotExist:
                membership = Membership.objects.create(
                user = request.user,
                plans = plans
                )
                context = {
                    'plans':plans,
                    'membership':membership
                }
                return render(request,'vpn/profile.html',context)
    else:
        messages.error(request, "Please Login to choose the plans")
        return redirect('sign-in')


class CreateCheckoutSession(View):
    """This class is used to to create checkout session for stripe"""

    def post(self, *args, **kwargs):
        host =self.request.get_host()
        vpn_id = self.request.POST.get('vpn-id')
        membership = Membership.objects.get(id = vpn_id)
        membership.sluged = membership.slug()
        membership.save()
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price_data':{
                        'currency' : 'usd',
                        'unit_amount':membership.plans.price*100,
                        'product_data': {
                            'name': membership.slug(),
                            },
                    },

                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url="http://{}{}".format(host,'/payment-success'),
            cancel_url="http://{}{}".format(host,'/payment-cancel'),
        )
        return redirect(checkout_session.url, code=303)


def payment_succes(request):
    """After the payment is successfully done user will redirected to success page"""

    context ={
        'payment_status':'success'
    }
    return render(request,'vpn/success.html',context)


def payment_cancel(request):
    """If the Payment is cancel or some issue happens user will be directed to this page"""

    context ={
        'payment_status':'cancel'
    }
    return render(request,'vpn/cancel.html',context)


#The endpoint_secret gets the webhook secret key of strip from the settings(global variable)
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
@csrf_exempt
def my_webhook_view(request):
    """Stripe Webhook used"""
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        if session.payment_status == "paid":
            line_item = session.list_line_items(session.id, limit=1).data[0]
            member_id = line_item['description']
            # Fulfill the purchase...
            fulfill_order(member_id)
        elif session.payment_status == "unpaid":
            line_item = session.list_line_items(session.id, limit=1).data[0]
            member_id = line_item['description']
            fail_payment(member_id)

    # Passed signature verification
    return HttpResponse(status=200)


def fulfill_order(member_id):
    """This function is used to update the membership models values"""
    date_object = datetime.date.today()
    membership =Membership.objects.get(sluged = member_id)
    month_after = date_object + relativedelta(months=+membership.plans.plan_duration_months)
    membership.premium = True
    membership.payment_completed = True
    membership.subscription_date = date_object
    membership.expiration_data = month_after
    membership.save()


def fail_payment(member_id):
    """
    On failure of payment the member who is created will be deleted
    he/she have to do payment again
    """
    membership =Membership.objects.get(sluged = member_id)
    membership.delete()