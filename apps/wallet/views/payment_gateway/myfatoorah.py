import requests
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect

from apps.shop.models.billing import Invoice
from apps.shop.models.shop import *
from core.utils.notification import notify_user_ticket
from digit_ydoob import settings


def PaymentMyFatoorah(request, slug):
    order_id = id
    if Order.objects.all().filter(slug=slug,order_status='Pending',source='Web',ordered=False).exists():
        old_orde = Order.objects.get(slug=slug,order_status='Pending',source='Web',ordered=False)
        # payment_method = Payment.objects.get(order=old_orde)
        order_details = OrderItem.objects.filter(
            order=old_orde).last()
        total = float(old_orde.total)

        url = f"{settings.FATOORAHBASURL}/SendPayment"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.MyFATOORAH_API_KEY}"
        }
        callback_url = reverse('home:ApiCallbackUrlMyFatoorah')

        data = {
            "CustomerName": f"{old_orde.owner.first_name} {old_orde.owner.last_name}",
            "NotificationOption": "LNK",
            "CustomerEmail": old_orde.owner.email,
            "InvoiceValue": total,
            "DisplayCurrencyIso": settings.FATOORAH_CURREENCY,
            # "CallBackUrl": f"{request.scheme}://{request.get_host()}"+callback_url,
            "CallBackUrl": f"{settings.FATOORAHBACKURL}",
            "ErrorUrl": f"{settings.FATOORAHERRORURL}",
            "Language": "AR",
            "InvoiceItems": [
                {
                    "ItemName": f"{old_orde.serial_no}",
                    "Quantity": old_orde.quantity,
                    "UnitPrice": total,
                    "Weight": 33,
                    "Width": 44,
                    "Height": 44,
                    # "Quantity": order_details.quantity,
                    # "UnitPrice": order_details.price,
                    # "Weight": order_details.product.PRDWeight,
                    # "Width": order_details.product.width,
                    # "Height": order_details.product.height,

                    "Depth": 30
                },

            ],
            # "ShippingMethod": 1,
            # "ShippingConsignee": {
            #     "PersonName":  f"{payment_method.first_name} {payment_method.last_name}",
            #     "Mobile": int(payment_method.phone),
            #     "EmailAddress": payment_method.Email_Address,
            #     "LineAddress": payment_method.street_address,
            #     "CityName": payment_method.state,
            #     "PostalCode": payment_method.post_code,
            #     "CountryCode": payment_method.country_code
            # },
            "SourceInfo": "string"
        }
        response = requests.post(url, headers=headers, json=data).json()

        if response:
            invoice_url = response['Data']['InvoiceURL']
            invoice_id = response['Data']['InvoiceId']
            message = response['Message']
            is_success = response['IsSuccess']

            invoice = Invoice(
                sender_model=ContentType.objects.get(model='Order'),sender_id=old_orde.id,
                owner_model=ContentType.objects.get(model='User'),owner_id=old_orde.owner.id,
                title=f"Order {old_orde.serial_no} Invoice",number=invoice_id,url=invoice_url,
                created_by='MyFatoorah Payment Gateway',message=message,is_success=is_success

            )
            invoice.save()
            # return HttpResponse("Payment data has been sent successfully.")
            return redirect(invoice_url)
        else:
            return HttpResponse("An error occurred while sending the payment data.")


def ApiCallbackUrlMyFatoorah(request, *args, **kwargs):
    if request.method == 'GET':

        payment_id = request.GET.get('paymentId')

        url = f"{settings.FATOORAHBASURL}/GetPaymentStatus"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.MyFATOORAH_API_KEY}"
        }
        callback_url = reverse('home:ApiCallbackUrlMyFatoorah')

        data = {

            "Key": f"{payment_id}",
            "KeyType": "paymentid"
        }

        response = requests.post(url, headers=headers, json=data).json()
        # print(response)
        if response:
            try:
                invoice_id = response['Data']['InvoiceId']
                invoice_status = response['Data']['InvoiceStatus']

                if invoice_status == "Paid":


                    if Invoice.objects.all().filter(number=invoice_id).exists():
                        old_invoice = Invoice.objects.get(number=invoice_id)
                        old_order = Order.objects.get(
                            id=old_invoice.sender_id)
                        payment = Payment(
                            sender_model=ContentType.objects.get(model='Invoice'),sender_id=old_invoice.id,
                            receiver_model=ContentType.objects.get(model='Order'),receiver_id=old_order.id,
                            owner_model=ContentType.objects.get(model='User'),owner_id=old_invoice.owner_id,
                            amount=old_order.total,payment_status='Completed',payment_method='Online Payment',
                            payment_gateway='MyFatoorah',api_id=payment_id,
                        )
                        payment.save()

                        old_order.payment_method = 'Online Payment'
                        old_order.payment_status = 'Complete'
                        old_order.order_status = 'OnShipping'
                        old_order.ordered = True
                        old_order.save()


                        try:
                            message = f"Your order has been successfully purchased, Order ID {old_order.id}."
                            notify_user_ticket(request, old_order.owner.email, message)
                            # send_mail(
                            #     'Great! Order ID{}. has been successfully purchased'.format(
                            #         old_orde.id),
                            #     ' Congratulations, you have made your order, This order will be delivered to you soon.',
                            #     f'{settings.EMAIL_SENDGRID}',
                            #     [f'{payment_method.Email_Address}'],
                            #     fail_silently=False,
                            # )
                        except:
                            pass

                        return redirect('home:PaymentSuccess')

                else:
                    messages.warning(
                        request, f"A technical problem has occurred, please contact technical support")
                    return redirect('home:cancel')
            except:
                messages.warning(
                    request, f"A technical problem has occurred, please contact technical support")
                return redirect('home:cancel')
        else:
            messages.warning(
                request, f"A technical problem has occurred, please contact technical support")
            return redirect('home:cancel')

    messages.warning(
        request, f"A technical problem has occurred, please contact technical support")
    return redirect('home:cancel')





# class PaymentMyFatoorah(LoginRequiredMixin, View):
#     '''
#     Handle Stripe payment (Stripe API)
#     '''
#
#     def get(self, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False,)
#         context = {
#             'STRIPE_PUBLIC_KEY': settings.MyFatoorah_api_key,
#             'order': order
#         }
#         return render(self.request, 'payments/PaymentMyFatoorah.html', context)
#
#     # Call API Function
#     def call_api(api_url, api_key, request_data, request_type="POST"):
#         request_data = json.dumps(request_data)
#         headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
#         try:
#             response = requests.request(request_type, api_url, data=request_data, headers=headers)
#         except:
#             print("An Error has occurred. Kindly check your API URL")
#             exit()
#         handle_response(response)
#         return response
#
#
# def handle_response(response):
#     try:     # Check if the response is a correct json file
#         response_data = response.json()
#         if "IsSuccess" in response_data.keys() and response_data["IsSuccess"] == True: #Suc
#             return
#         elif "ValidationErrors" in response_data.keys() and response_data["ValidationErrors"] != None:
#             error = []
#             for i in range(len(response_data["ValidationErrors"])):
#                 v_error = [response_data["ValidationErrors"][i]["Name"], response_data["ValidationErrors"][i]["Error"]]
#                 error.append(v_error)
#         elif "ErrorMessage" in response_data.keys() and response_data["ErrorMessage"] != None:
#             error = response_data["ErrorMessage"]
#         elif "Message" in response_data.keys() and response_data["Message"] != None:
#             error = response_data["Message"]
#     except:
#         if response.text == "": # In case of empty response
#             error = "API key or API URL is not correct"
#         else:
#             error = "An Error has occuered. API response: ", response.text
#     print(error)
#     exit()