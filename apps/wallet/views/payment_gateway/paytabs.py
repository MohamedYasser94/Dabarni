import logging
from datetime import timezone

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

from apps.classified.models.models import JobProgress
from apps.wallet.models.payment import Payment
from apps.wallet.models.billing import Purchase, Invoice
from core.utils.notification import notify_user_ticket

logger = logging.getLogger(__name__)


######################## For App Flutter
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_paytabs_keys(request):
    """
    API endpoint to securely provide PayTabs keys to the Flutter app.
    """
    try:
        keys = {
            "profile_id": settings.PAYTABS_PROFILE_ID,
            "server_key": settings.PAYTABS_SERVER_KEY,
            "client_key": settings.PAYTABS_CLIENT_KEY  # <-- ADD CLIENT KEY TO YOUR settings.py
        }
        return Response(keys, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        job_request = JobProgress.objects.filter(slug=order_slug).first()
        if not job_request:
            return JsonResponse({'status': 'error', 'message': 'Job request not found'}, status=404)

        amount = job_request.price
        if not amount or float(amount) <= 0:
            return JsonResponse({'status': 'error', 'message': 'Invalid amount'}, status=400)

        # URLs
        url = settings.PAYTABS_URL
        print('url',url)
        profile_id = settings.PAYTABS_PROFILE_ID
        server_key = settings.PAYTABS_SERVER_KEY
        callback_url = settings.PAYTABS_CALLBACK_URL

        # return_url يختلف حسب المصدر
        tran_ref = request.data.get('tran_ref', 'default_tran_ref')
        if platform == 'app':
            return_url = f"manfz://payment-success?status=success"
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
                "street1": "N/A",
                "country": "EG",
                "city": "N/A",
                "state": "N/A",
                "zip": "12345",
            },
        }

        response = requests.post(url, headers={'Authorization': server_key}, json=payload)
        response_data = response.json()
        print(response_data)
        if response.status_code != 200:
            print('Error initiating payment with PayTabs:', response_data.get('message', 'Unknown error'))
            return JsonResponse({
                'status': 'error',
                'message': response_data.get('message', 'Failed to initiate payment with PayTabs.'),
                'details': response_data,
            }, status=400)

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
            job_request = JobProgress.objects.get(slug=order_slug)

            if response_status == 'A':  # 'A' for Approved
                job_request.payment_status = "Complete"
                job_request.Progress = "Active"  # Or whatever status is appropriate
                job_request.save()
            else:
                job_request.payment_status = "Failed"
                job_request.save()

            return JsonResponse({'status': 'success'})
        except JobProgress.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)



@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ApiJobsPaymentStatusUpdate(request):
    """
    Handles the successful payment confirmation from the Flutter app.
    Updates the JobRequest and creates associated Purchase and Invoice records.
    """
    if request.method == 'POST':
        try:
            data = request.data
            order_slug = data.get('order_slug')
            tran_ref = data.get('tran_ref')

            if not order_slug or not tran_ref:
                return Response({"detail": "order_slug and tran_ref are required."}, status=status.HTTP_400_BAD_REQUEST)

            job_request = JobProgress.objects.filter(slug=order_slug, user=request.user).first()

            if not job_request:
                return Response({"detail": "Job request not found or you do not have permission."},
                                status=status.HTTP_404_NOT_FOUND)

            if job_request.payment_status == 'Complete':
                return Response({"detail": "This order has already been paid."}, status=status.HTTP_200_OK)

            # 1. Update the JobRequest
            job_request.payment_status = "Complete"
            job_request.progress = "Pending"
            # Use the actual price from the job request, not final_price which might be null
            job_request.final_price = job_request.price
            job_request.save()

            # 2. Create the Purchase record
            # CORRECTED: Use request.user directly
            user = request.user

            try:
                purchase = Purchase.objects.filter(
                    owner_model=ContentType.objects.get(model='User'),
                    owner_id=user.id,
                                                    sender_model=ContentType.objects.get(model='JobRequest'),
                                                    sender_id=job_request.id,
                                                   ).first()
                if purchase:
                    purchase.amount = job_request.final_price
                    purchase.purchase_status = "Received"
                    purchase.payment_status = "Completed"
                    purchase.tracking_no = tran_ref
                    purchase.save()

            except Purchase.DoesNotExist:

                purchase = Purchase.objects.create(
                    sender_model=ContentType.objects.get(model='JobRequest'),
                    sender_id=job_request.id,
                    # Assuming the receiver is the provider of the job
                    receiver_model=ContentType.objects.get(model='JobProvider'),
                    receiver_id=job_request.classified_job.provider.id,
                    owner_model=ContentType.objects.get(model='User'),
                    owner_id=user.id,
                    amount=job_request.final_price,
                    purchase_status="Received",
                    payment_status="Completed",
                    tracking_no=tran_ref,
                    source='App',
                    purchase_date=timezone.now(),
                )

            # 3. Create the Invoice and Payment records
            invoice = Invoice.objects.create(
                sender_model=ContentType.objects.get(model='Purchase'),
                sender_id=purchase.id,
                owner_model=ContentType.objects.get(model='User'),
                owner_id=user.id,
                title=f"Purchase {purchase.serial_no} Invoice",
                created_by='PayTabs System',
                gateway_transaction=tran_ref,
                is_success=True,
                message="Payment successful via app."
            )
            Payment.objects.create(
                sender_model=ContentType.objects.get(model='Invoice'),
                sender_id=invoice.id,
                receiver_model=ContentType.objects.get(model='Purchase'),
                receiver_id=purchase.id,
                owner_model=ContentType.objects.get(model='User'),
                owner_id=user.id,
                amount=purchase.amount,
                payment_status='Completed',
                payment_method='Online Payment',
                payment_gateway='PayTabs',
                gateway_transaction=tran_ref
            )

            return Response({"detail": "Payment status updated and records created successfully."},
                            status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error in ApiJobsPaymentStatusUpdate: {str(e)}")
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ApiJobsPaymentStatusFailed(request):
    """
    Handles a payment failure or cancellation confirmation from the app.
    Marks the associated JobRequest as 'Canceled'.
    """
    if request.method == 'POST':
        try:
            data = request.data
            order_slug = data.get('order_slug')

            if not order_slug:
                return Response({"detail": "order_slug is required."}, status=status.HTTP_400_BAD_REQUEST)

            job_request = JobProgress.objects.filter(slug=order_slug, user=request.user).first()
            if not job_request:
                return Response({"detail": "Job request not found or you do not have permission."},
                                status=status.HTTP_404_NOT_FOUND)

            # Mark the request as canceled
            job_request.progress = 'Canceled'
            job_request.payment_status = 'Failed'
            job_request.save()

            return Response({"detail": "Job request marked as canceled successfully."},
                            status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error in ApiJobsPaymentStatusFailed: {str(e)}")
            return Response({"detail": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"detail": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)