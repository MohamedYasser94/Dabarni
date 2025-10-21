import logging

from django.http import HttpResponseRedirect


from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import requests
import json

from rest_framework.response import Response

from apps.wallet.models.payment import Payment
from apps.wallet.models.billing import Purchase, Invoice
from core.utils.notification import notify_user_ticket

logger = logging.getLogger(__name__)
def payment_paytabs(request, slug):
    """
    Initiates a payment request with PayTabs.
    """
    if Purchase.objects.filter(slug=slug, purchase_status='Pending', source='Web', ).exists():
        purchase = Purchase.objects.get(slug=slug, purchase_status='Pending', source='Web', )

        # PayTabs API endpoint
        url = "https://secure-egypt.paytabs.com/payment/request"

        # Required parameters for PayTabs
        payload = {
            "profile_id": settings.PAYTABS_PROFILE_ID,
            "tran_type": "sale",
            "tran_class": "ecom",
            "cart_id": str(purchase.id),
            "cart_description": f"Order #{purchase.serial_no}",
            "cart_currency": "EGP",
            "cart_amount": float(purchase.amount),
            "callback": settings.PAYTABS_CALLBACK_URL,
            "return": settings.PAYTABS_RETURN_URL,
            "customer_details": {
                "name": f"{purchase.owner.first_name} {purchase.owner.last_name}",
                "email": purchase.owner.email,
                "phone": purchase.owner.phone,
                "street1": 'SA Defult Street',
                "city": 'SA',
                "state":'SA',
                "country": "EG",
                "zip": "00000"
            }
        }

        # Sending the request to PayTabs
        response = requests.post(url, headers={'Authorization': settings.PAYTABS_SERVER_KEY}, json=payload)
        response_data = response.json()

        if response.status_code == 200 and 'redirect_url' in response_data:
            # Create Invoice and Payment records
            invoice = Invoice.objects.create(
                sender_model=ContentType.objects.get(model='Purchase'),
                sender_id=purchase.id,
                owner_model=ContentType.objects.get(model='User'),
                owner_id=purchase.owner.id,
                title=f"Purchase {purchase.serial_no} Invoice",
                created_by='PayTabs System',
            )
            Payment.objects.create(
                sender_model=ContentType.objects.get(model='Invoice'),
                sender_id=invoice.id,
                receiver_model=ContentType.objects.get(model='Purchase'),
                receiver_id=purchase.id,
                owner_model=ContentType.objects.get(model='User'),
                owner_id=invoice.owner_id,
                amount=purchase.amount,
                payment_status='Pending',
                payment_method='Online Payment',
                payment_gateway='PayTabs',
            )
            # Redirect to PayTabs payment page
            print('Redirecting to PayTabs payment page...')
            print('Redirect URL:', response_data['redirect_url'])
            print('Payment reference:', response_data)
            return HttpResponseRedirect(response_data['redirect_url'])
        else:
            messages.error(request, "Failed to initiate payment with PayTabs.")
            print('Error initiating payment with PayTabs:', response_data.get('message', 'Unknown error'))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    else:
        messages.warning(request, 'Please enter your information correctly.')
        print('Purchase not found or not in pending status.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@csrf_exempt
def api_callback_url_paytabs(request):
    """
    Handles the callback from PayTabs after a payment attempt.
    """
    print('api_callback_url_paytabs Received callback from PayTabs...', request.method, request.body, request.META.get('HTTP_REFERER'))
    if request.method == 'POST':
        callback_data = json.loads(request.body)
        cart_id = callback_data.get('cart_id')
        tran_ref = callback_data.get('tran_ref')
        payment_result = callback_data.get('payment_result', {})
        response_status = payment_result.get('response_status')

        if Purchase.objects.filter(id=cart_id).exists():
            purchase = Purchase.objects.get(id=cart_id)
            invoice = Invoice.objects.get(sender_model=ContentType.objects.get(model='Purchase').id, sender_id=purchase.id)
            payment = Payment.objects.get(sender_id=invoice.id)

            if response_status == 'A':  # 'A' for Approved
                print('Payment approved.' ,response_status)
                purchase.ordered = True
                purchase.purchase_status = "Received"
                purchase.payment_status = "Completed"
                purchase.tracking_no = tran_ref  # Using tran_ref as tracking number
                purchase.save()

                invoice.is_success = True
                invoice.message = "Payment Successfully"
                invoice.number = tran_ref
                invoice.save()

                payment.payment_status = 'Completed'
                payment.gateway_transaction = tran_ref
                payment.save()

                # Notify user
                try:
                    message = f"Your order has been successfully purchased. Order ID: {purchase.id}."
                    notify_user_ticket(request, purchase.owner.email, message)
                except Exception as e:
                    print(f"Error sending notification: {e}")

                return redirect('home:PaymentSuccess')
            else:
                purchase.order_status = "Failed"
                purchase.payment_status = "Failed"
                purchase.save()

                invoice.is_success = False
                invoice.message = payment_result.get('response_message', 'Payment Failed')
                invoice.save()

                payment.payment_status = 'Failed'
                payment.save()

                messages.warning(request, "Payment failed. Please try again.")
                return redirect('home:cancel')

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def api_initiate_paytabs_payment(request):
    logger.debug(f"Request data: {request.data}")
    logger.debug(f"Authenticated user: {request.user}")

    order_slug = request.data.get('order_slug')
    platform = request.data.get('platform', 'web')  # ← نضيف باراميتر المنصة
    cart_description = request.data.get('cart_description', f"Order #{order_slug}")
    name = request.data.get('name', 'Guest')
    email = request.data.get('email', 'guest@example.com')
    phone = request.data.get('phone', '1111111')

    if not order_slug:
        return JsonResponse({'status': 'error', 'message': 'Missing order_slug'}, status=400)

    try:
        job_request = JobRequest.objects.filter(slug=order_slug).first()
        if not job_request:
            return JsonResponse({'status': 'error', 'message': 'Job request not found'}, status=404)

        amount = job_request.price
        if not amount or float(amount) <= 0:
            return JsonResponse({'status': 'error', 'message': 'Invalid amount'}, status=400)

        # URLs
        url = settings.PAYTABS_URL
        profile_id = settings.PAYTABS_PROFILE_ID
        server_key = settings.PAYTABS_SERVER_KEY
        callback_url = settings.PAYTABS_CALLBACK_URL

        # return_url يختلف حسب المصدر
        if platform == 'app':
            return_url = f"manfz://payment-success?order_slug={order_slug}"
        else:
            return_url = settings.PAYTABS_RETURN_URL

        payload = {
            "profile_id": profile_id,
            "tran_type": "sale",
            "tran_class": "ecom",
            "cart_id": str(order_slug),
            "cart_description": cart_description,
            "cart_currency": "EGP",
            "cart_amount": float(amount),
            "callback": callback_url,
            "return": return_url,
            "hide_shipping" : True,  # Hide shipping details if not needed
            "customer_details": {
                "name": name,
                "email": email,
                "phone": phone,
                "street1": "Default Street",
                "city": "Cairo",
                "state": "Cairo",
                "country": "EG",
                "zip": "12345",
            },
        }

        response = requests.post(url, headers={'Authorization': server_key}, json=payload)
        response_data = response.json()

        if response.status_code == 200 and 'redirect_url' in response_data:
            return JsonResponse({
                'status': 'success',
                'redirect_url': response_data['redirect_url'],
                'tran_ref': response_data.get('tran_ref'),
                'return_url': return_url,
                'callback_url': callback_url,
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': response_data.get('message', 'Failed to initiate payment with PayTabs.'),
                'details': response_data,
            }, status=400)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Server error: {e}'}, status=500)


@csrf_exempt
def api_callback_url_paytabs(request):
    """
    Handles the server-to-server callback from PayTabs to update the order status.
    """
    if request.method == 'POST':
        callback_data = json.loads(request.body)
        order_slug = callback_data.get('cart_id')
        payment_result = callback_data.get('payment_result', {})
        response_status = payment_result.get('response_status')

        try:
            job_request = JobRequest.objects.get(slug=order_slug)

            if response_status == 'A':  # 'A' for Approved
                job_request.payment_status = "Complete"
                job_request.Progress = "Active"  # Or whatever status is appropriate
                job_request.save()
            else:
                job_request.payment_status = "Failed"
                job_request.save()

            return JsonResponse({'status': 'success'})
        except JobRequest.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)