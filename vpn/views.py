from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .forms import CustomUserCreationForm, NewsLetterForm, ContactForm
from .models import Plan, Membership
from django.contrib.auth.models import User
import stripe
from django.conf import settings
from django.views.generic import View
import datetime
from dateutil.relativedelta import relativedelta

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def news_letter_view(request):
    form = NewsLetterForm()
    if request.method == "POST":
        form = NewsLetterForm(request.POST)
        if form.is_valid():
            form.save()
    context ={
        "form": form
    }
    return render(request,'main.html', context)

def contact_view(request):
    contact_form = ContactForm()
    if request.method == "POST":
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact_form.save()
    context ={
        "contact_form": contact_form
    }
    return render(request,'main.html', context)

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
    return render(request, 'vpn/signup.html', context)

def logoutUser(request):
    logout(request)
    messages.error(request, 'User was successfully logout')
    return redirect('sign-in')


@login_required(login_url='sign-in')
def profile_management(request):
    fname = request.user
    email = request.user.email
    membership = Membership.objects.get(user = fname)
    context = {
        'fname': fname,
        'email': email,
        'membership' : membership
    }
    return render(request, 'vpn/profile.html', context)

@login_required(login_url='sign-in')
def checkout(request,pk):
    """This is the checkout page that will tell us which plan the user opt"""

    if request.user.is_authenticated:
        plans = Plan.objects.get(id=pk)
        if plans.price != 0:
            try:
                date_object = datetime.date.today()
                month_after = date_object + relativedelta(months=+plans.plan_duration_months)
                membership = Membership.objects.get(user = request.user)
                membership.plans = plans
                membership.subscription_date = date_object
                membership.expiration_data = month_after
                membership.save()
                context = {
                    'plans':plans,
                    'membership':membership
                }
                return render(request, 'vpn/checkout_view.html', context)

            except Membership.DoesNotExist:
                date_object = datetime.date.today()
                month_after = date_object + relativedelta(months=+plans.plan_duration_months)
                membership = Membership.objects.create(
                user = request.user,
                plans = plans,
                subscription_date = date_object,
                expiration_data = month_after
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

    
    return render(request,'vpn/success.html')


def payment_cancel(request):
    """If the Payment is cancel or some issue happens user will be directed to this page"""

    return render(request,'vpn/cancel.html')


#The endpoint_secret gets the webhook secret key of strip from the settings(global variable)
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
@csrf_exempt
def my_webhook_view(request):
    """Stripe Webhook used"""
    payload = request.body
    sig_header = request.headers['STRIPE_SIGNATURE']
    print(sig_header)
    event = None
    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(e,status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(e,status=400)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        if session.payment_status == "paid":
            line_item = session.list_line_items(session.id, limit=1).data[0]
            member_id = line_item['description']
            print(line_item)
            print(session.payment_status)
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
    membership.premium_membership = True
    membership.payment_completed = True
    membership.subscription_date = date_object
    membership.expiration_data = month_after
    membership.save()


def fail_payment(member_id):
    """
    On failure of payment the member(Model) who is being created will be deleted
    he/she have to do payment again
    """
    membership =Membership.objects.get(sluged = member_id)
    membership.delete()

'''def stripe_balance(request):
    report  = stripe.BalanceTransaction.list(limit=3)
    print(report)'''

#All the chart section code will be as followed
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import  F, Sum, Avg
from django.db.models.functions import ExtractYear, ExtractMonth
from django.http import JsonResponse
from vpn.api.utils import months, colorPrimary, colorSuccess, colorDanger, generate_color_palette, get_year_dict


@staff_member_required
def get_filter_options(request):
    grouped_memberships = Membership.objects.annotate(year=ExtractYear('subscription_date')).values('year').order_by('-year').distinct()
    options = [membership['year'] for membership in grouped_memberships]

    return JsonResponse({
        'options': options,
    })


@staff_member_required
def get_sales_chart(request, year):
    memberships = Membership.objects.filter(subscription_date__year=year)
    grouped_purchases = memberships.annotate(price=F('plans__price')).annotate(month=ExtractMonth('subscription_date'))\
        .values('month').annotate(average=Sum('plans__price')).values('month', 'average').order_by('month')

    sales_dict = get_year_dict()

    for group in grouped_purchases:
        sales_dict[months[group['month']-1]] = round(group['average'], 2)

    return JsonResponse({
        'title': f'Sales in {year}',
        'data': {
            'labels': list(sales_dict.keys()),
            'datasets': [{
                'label': 'Gross Amount ($)',
                'backgroundColor': colorPrimary,
                'borderColor': colorPrimary,
                'data': list(sales_dict.values()),
            }]
        },
    })

@staff_member_required
def spend_per_customer_chart(request, year):
    purchases = Membership.objects.filter(subscription_date__year=year)
    grouped_purchases = purchases.annotate(price=F('plans__price')).annotate(month=ExtractMonth('subscription_date'))\
        .values('month').annotate(average=Avg('plans__price')).values('month', 'average').order_by('month')

    spend_per_customer_dict = get_year_dict()

    for group in grouped_purchases:
        spend_per_customer_dict[months[group['month']-1]] = round(group['average'], 2)

    return JsonResponse({
        'title': f'Spend per customer in {year}',
        'data': {
            'labels': list(spend_per_customer_dict.keys()),
            'datasets': [{
                'label': 'Amount ($)',
                'backgroundColor': colorPrimary,
                'borderColor': colorPrimary,
                'data': list(spend_per_customer_dict.values()),
            }]
        },
    })


@staff_member_required
def payment_success_chart(request, year):
    membership = Membership.objects.filter(subscription_date__year=year)

    return JsonResponse({
        'title': f'Payment success rate in {year}',
        'data': {
            'labels': ['Successful', 'Unsuccessful'],
            'datasets': [{
                'label': 'Amount ($)',
                'backgroundColor': [colorSuccess, colorDanger],
                'borderColor': [colorSuccess, colorDanger],
                'data': [
                    membership.filter(payment_completed=True).count(),
                    membership.filter(payment_completed=False).count(),
                ],
            }]
        },
    })

