from datetime import time

from bs4 import BeautifulSoup
from django.conf import settings
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.utils import json

from apps.catalog.models.models import Products
from apps.shop.models.Payment import Payment
from apps.shop.models.billing import Invoice
from apps.shop.models.shop import Order, OrderItem
from apps.shop.views.utils import code_generator
from core.utils.notification import notify_user_ticket


def PaymentPayMob(request, slug):
    context = None
    # if request.method == "POST":
    order_id = id
    if Order.objects.all().filter(slug=slug, order_status='Pending', source='Web', ordered=False).exists():
        old_orde = Order.objects.get(slug=slug, order_status='Pending', source='Web', ordered=False)
        # payment_method = Payment.objects.get(order=old_orde)
        order_details = OrderItem.objects.filter(
            order=old_orde).last()
        # endpoint for get account token "Authentication Request"
        url_authentication = "https://accept.paymob.com/api/auth/tokens"
        data_authentication = {
            "api_key": settings.PAYMOB_API_KEY
        }
        request_api_token = requests.post(
            url_authentication, json=data_authentication).json()
        account_token = request_api_token["token"]

        merchant_order_id = f'{old_orde.serial_no}-{code_generator()}'

        total = int(float(old_orde.total)*100)

        url_order_registration = "https://accept.paymob.com/api/ecommerce/orders"
        data_order_registration = {
            "auth_token": account_token,
            "delivery_needed": "false",
            "amount_cents": f"{total}",
            "currency": "EGP",
            "merchant_order_id": merchant_order_id,
            "items": [
                {
                    "name": f"{old_orde.serial_no}",
                    "amount_cents": f"{total}",
                    "description": f"{old_orde.serial_no}",
                    "quantity": "1"
                }
            ],
            "shipping_data": {},
            "shipping_details": {}
        }
        request_order_registration = requests.post(
            url_order_registration, json=data_order_registration).json()

        order_registration_id = request_order_registration["id"]
        # Payment Key Request
        url_payment_key = "https://accept.paymob.com/api/acceptance/payment_keys"
        data_payment_key = {
            "auth_token": account_token,
            "amount_cents": f"{total}",
            "expiration": 3600,
            "order_id": f"{order_registration_id}",
            "billing_data": {
                "apartment": "None",
                "email": old_orde.owner.email,
                "floor": "None",
                "first_name": old_orde.owner.first_name,
                "street": old_orde.address.address,
                "building": "None",
                "phone_number": old_orde.address.phone,
                "shipping_method": "PKG",
                "postal_code": "None",
                "city": "None",
                "country": "eg",
                "last_name": old_orde.owner.last_name,
                "state": old_orde.address.governorates
            },
            "currency": "EGP",
            "integration_id": settings.PAYMOB_INTEGRATION_ID,
            "lock_order_when_paid": "false"
        }
        request_payment_key = requests.post(
            url_payment_key, json=data_payment_key).json()



        payment_key_token = request_payment_key["token"]
        # merchant_order_id and order_registration_id will used to get booking order
        invoice = Invoice(
            sender_model=ContentType.objects.get(model='Order'), sender_id=old_orde.id,
            owner_model=ContentType.objects.get(model='User'), owner_id=old_orde.owner.id,
            title=f"Order {old_orde.serial_no} Invoice", account_token=account_token,
            merchant=merchant_order_id, registration=order_registration_id,
            created_by='PayMob System',

        )
        invoice.save()
        payment_method = Payment(
            sender_model=ContentType.objects.get(model='Invoice'), sender_id=invoice.id,
            receiver_model=ContentType.objects.get(model='Order'), receiver_id=old_orde.id,
            owner_model=ContentType.objects.get(model='User'), owner_id=invoice.owner_id,
            amount=old_orde.total, payment_status='Completed', payment_method='Online Payment',
            payment_gateway='PayMob',
        )
        payment_method.save()


        # car_booking.

        return HttpResponseRedirect(f"https://accept.paymob.com/api/acceptance/iframes/892306?payment_token={payment_key_token}")

    else:
        messages.warning(request, 'Please enter your information correctly.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def ApiCallbackUrlPayMob(request, *args, **kwargs):

    if request.method == 'GET':
        order_id_paymob = request.GET['order']
        merchant_order_id = request.GET['merchant_order_id']
        trnx_id = int(request.GET['id'])

        if Invoice.objects.all().filter(registration=order_id_paymob, merchant=merchant_order_id).exists():
            old_invoice = Invoice.objects.get(registration=order_id_paymob, merchant=merchant_order_id)
            old_order = Order.objects.get(id = old_invoice.sender_id)


            # Retrieve A Transaction
            url_retrieve_transaction = f"https://accept.paymob.com/api/acceptance/transactions/{trnx_id}"
            data_retrieve_transaction = {
                "auth_token": f"{old_invoice.account_token}"
            }
            request_order_registration = requests.get(
                url_retrieve_transaction, json=data_retrieve_transaction).json()


            transaction_id = int(request_order_registration["id"])
            if transaction_id == trnx_id:
                old_order.trnx_id = trnx_id
                if request_order_registration["success"] == True:
                    # checkout success

                    try:
                        Consignee_id = old_order.user.id
                        Consignee_email = old_order.user.email
                    except:
                        pass
                    payment_method = Payment.objects.get(sender_id=old_invoice.id)
                    old_invoice.number = trnx_id
                    old_invoice.is_success = True
                    old_invoice.message = "Payment Successfully"
                    old_invoice.save()




                    if settings.ARAMEX_USERNAME != "":
                        if old_order.address.country == settings.ARAMEX_ACCOUNTCOUNTRYCODE:
                            product_group = "DOM"
                            product_type = "OND"
                        else:
                            product_group = "EXP"
                            product_type = "PPX"
                        data = {
                            "ClientInfo": {
                                "UserName": f"{settings.ARAMEX_USERNAME}",
                                "Password": f"{settings.ARAMEX_PASSWORD}",
                                "Version": f"{settings.ARAMEX_VERSION}",
                                "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                                "AccountPin": f"{settings.ARAMEX_ACCOUNTPIN}",
                                "AccountEntity": f"{settings.ARAMEX_ACCOUNTENTITY}",
                                "AccountCountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                                "Source": f"{settings.ARAMEX_SOURCE}"

                            },

                            "LabelInfo": {
                                "ReportID": 9201,
                                "ReportType": "URL"
                            },
                            "Shipments": [
                                {
                                    "Reference1": f"{old_order}",
                                    "Reference2": "",
                                    "Reference3": "",
                                    "Shipper": {
                                        "Reference1": f"{old_order}",
                                        "Reference2": "",
                                        "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                                        "PartyAddress": {
                                            "Line1": "Oman",
                                            "Line2": "",
                                            "Line3": "",
                                            "City": "Oman",
                                            "StateOrProvinceCode": "",
                                            "PostCode": "",
                                            "CountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                                            "Longitude": 0,
                                            "Latitude": 0,
                                            "BuildingNumber": None,
                                            "BuildingName": None,
                                            "Floor": None,
                                            "Apartment": None,
                                            "POBox": None,
                                            "Description": "alithemes.com product"
                                        },
                                        "Contact": {
                                            "Department": "",
                                            "PersonName": "alithemes.com store",
                                            "Title": "",
                                            "CompanyName": "alithemes.com",
                                            "PhoneNumber1": "1111111111",
                                            "PhoneNumber1Ext": "",
                                            "PhoneNumber2": "",
                                            "PhoneNumber2Ext": "",
                                            "FaxNumber": "",
                                            "CellPhone": "1111111111111",
                                            "EmailAddress": "mail@alithemes.com",
                                            "Type": ""
                                        }
                                    },
                                    "Consignee": {
                                        "Reference1": f"{Consignee_id}",
                                        "Reference2": f"{Consignee_email}",
                                        "AccountNumber": f"{Consignee_id}",
                                        "PartyAddress": {
                                            "Line1": f"{old_order.address.address}",
                                            "Line2": "",
                                            "Line3": "",
                                            "City": f"{old_order.address.City}",
                                            "StateOrProvinceCode": f"{old_order.address.state}",
                                            "PostCode": f"{old_order.address.post_code}",
                                            "CountryCode": f"{old_order.address.country}",
                                            "Longitude": 0,
                                            "Latitude": 0,
                                            "BuildingNumber": "",
                                            "BuildingName": "",
                                            "Floor": "",
                                            "Apartment": "",
                                            "POBox": None,
                                            "Description": "Please contact me when the shipment arrives"
                                        },
                                        "Contact": {
                                            "Department": "",
                                            "PersonName": f"{old_order.owner.first_name} {old_order.owner.last_name}",
                                            "Title": f"{old_order.owner.last_name}",
                                            "CompanyName": "",
                                            "PhoneNumber1": f"{old_order.address.phone}",
                                            "PhoneNumber1Ext": "",
                                            "PhoneNumber2": "",
                                            "PhoneNumber2Ext": "",
                                            "FaxNumber": "",
                                            "CellPhone": f"{old_order.address.phone}",
                                            "EmailAddress": f"{old_order.owner.email}",
                                            "Type": ""
                                        }
                                    },
                                    "ThirdParty": {
                                        "Reference1": "",
                                        "Reference2": "",
                                        "AccountNumber": "",
                                        "PartyAddress": {
                                            "Line1": "",
                                            "Line2": "",
                                            "Line3": "",
                                            "City": "",
                                            "StateOrProvinceCode": "",
                                            "PostCode": "",
                                            "CountryCode": "",
                                            "Longitude": 0,
                                            "Latitude": 0,
                                            "BuildingNumber": None,
                                            "BuildingName": None,
                                            "Floor": None,
                                            "Apartment": None,
                                            "POBox": None,
                                            "Description": None
                                        },
                                        "Contact": {
                                            "Department": "",
                                            "PersonName": "",
                                            "Title": "",
                                            "CompanyName": "",
                                            "PhoneNumber1": "",
                                            "PhoneNumber1Ext": "",
                                            "PhoneNumber2": "",
                                            "PhoneNumber2Ext": "",
                                            "FaxNumber": "",
                                            "CellPhone": "",
                                            "EmailAddress": "",
                                            "Type": ""
                                        }
                                    },
                                    "ShippingDateTime": str('/Date(' + str(time) + ')/'),
                                    "DueDate": str('/Date(' + str(time) + ')/'),
                                    "Comments": "",
                                    "PickupLocation": "",
                                    "OperationsInstructions": "",
                                    "AccountingInstrcutions": "",
                                    "Details": {
                                        "Dimensions": None,
                                        "ActualWeight": {
                                            "Unit": "KG",
                                            "Value": float(old_order.weight)
                                        },
                                        "ChargeableWeight": None,
                                        "DescriptionOfGoods": None,
                                        "GoodsOriginCountry": "IN",
                                        "NumberOfPieces": 1,
                                        "ProductGroup": product_group,
                                        "ProductType": product_type,
                                        "PaymentType": "P",
                                        "PaymentOptions": "",
                                        "CustomsValueAmount": None,
                                        "CashOnDeliveryAmount": None,
                                        "InsuranceAmount": None,
                                        "CashAdditionalAmount": None,
                                        "CashAdditionalAmountDescription": "",
                                        "CollectAmount": None,
                                        "Services": "",
                                        "Items": []
                                    },
                                    "Attachments": [],
                                    "ForeignHAWB": "",
                                    "TransportType ": 0,
                                    "PickupGUID": "",
                                    "Number": None,
                                    "ScheduledDelivery": None
                                }
                            ],
                            "Transaction": None

                        }

                        url = 'https://ws.aramex.net/ShippingAPI.V2/Shipping/Service_1_0.svc/json/CreateShipments'
                        r = requests.post(url, json=data)

                        soup = BeautifulSoup(r.content, 'html.parser')
                        # print(soup)
                        old_order.tracking_no = soup.id.string
                        old_order.rpt_cache = soup.labelurl.string

                    # delete available
                    # products_details = OrderItem.objects.all().filter(order=old_order)
                    # for pro in products_details:
                    #     product_order = Products.objects.get(
                    #         id=pro.product.id)
                    #     if product_order.available > 0:
                    #         product_order.available = product_order.available - pro.quantity
                    #         product_order.save()

                    old_order.ordered = True
                    old_order.order_status = "OnShipping"
                    old_order.payment_status = "Completed"
                    old_order.save()

                    # code for set supplier's balance
                    # obj_order_suppliers = OrderSupplier.objects.all().filter(order=old_orde)
                    # for obj_order_supplier in obj_order_suppliers:
                    #     supplier = Profile.objects.get(
                    #         id=obj_order_supplier.vendor.id)
                    #     supplier.blance = float(
                    #         supplier.blance) + float(obj_order_supplier.amount)
                    #     supplier.save()
                    try:

                        message = f"Your order has been successfully purchased, Order ID {old_order.id}."
                        notify_user_ticket(request, old_order.owner.email, message)
                    except:
                        pass
                    if "coupon_id" in request.session.keys():
                        del request.session["coupon_id"]

                    return redirect('home:PaymentSuccess')

                else:
                    messages.warning(
                        request, f"A technical problem has occurred, please contact technical support")
                    return redirect('home:cancel')
        else:
            messages.warning(
                request, f"A technical problem has occurred, please contact technical support")
            return redirect('home:homeIndex')


@csrf_exempt
def ApiCallbackUrlPayMobApp(request, *args, **kwargs):

    try:
       if request.method == 'POST':
           body_unicode = request.body.decode('utf-8')
           body = json.loads(body_unicode)
           payment_key = body['payment_key']
           order_slug = body['order_slug']
           merchant_order_id = body['merchant_order_id']
           transaction_id = body['transaction_id']
           order_id_paymob = body['order']
           success = body['success']
           response_code = body['response_code']
           message = body['message']



           if Order.objects.all().filter(slug=order_slug).exists():
               old_order = Order.objects.get(slug=order_slug)
               old_invoice = Invoice.objects.get(sender_model=ContentType.objects.get(model = 'Order').id, sender_id=old_order.id)


               # Retrieve A Transaction
               url_retrieve_transaction = f"https://accept.paymob.com/api/acceptance/transactions/{transaction_id}"
               data_retrieve_transaction = {
                   "auth_token": f"{payment_key}"
               }
               request_order_registration = requests.get(
                   url_retrieve_transaction, json=data_retrieve_transaction).json()



               transaction_id = (request_order_registration["id"])
               if transaction_id == transaction_id:

                   if request_order_registration["success"] == True:

                       try:
                           Consignee_id = old_order.user.id
                           Consignee_email = old_order.user.email
                       except:
                           pass
                       old_payment = Payment.objects.get(sender_id=old_invoice.id)
                       old_invoice.gateway_transaction = transaction_id
                       old_invoice.gateway_order = order_id_paymob
                       old_invoice.is_success = True
                       old_invoice.message = "Payment Successfully"
                       old_invoice.save()
                       old_payment.payment_status = 'Completed'
                       old_payment.gateway_transaction = transaction_id
                       old_payment.gateway_order = order_id_paymob
                       old_payment.save()

                       if settings.ARAMEX_USERNAME != "":
                           if old_order.address.country == settings.ARAMEX_ACCOUNTCOUNTRYCODE:
                               product_group = "DOM"
                               product_type = "OND"
                           else:
                               product_group = "EXP"
                               product_type = "PPX"
                           data = {
                               "ClientInfo": {
                                   "UserName": f"{settings.ARAMEX_USERNAME}",
                                   "Password": f"{settings.ARAMEX_PASSWORD}",
                                   "Version": f"{settings.ARAMEX_VERSION}",
                                   "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                                   "AccountPin": f"{settings.ARAMEX_ACCOUNTPIN}",
                                   "AccountEntity": f"{settings.ARAMEX_ACCOUNTENTITY}",
                                   "AccountCountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                                   "Source": f"{settings.ARAMEX_SOURCE}"

                               },

                               "LabelInfo": {
                                   "ReportID": 9201,
                                   "ReportType": "URL"
                               },
                               "Shipments": [
                                   {
                                       "Reference1": f"{old_order}",
                                       "Reference2": "",
                                       "Reference3": "",
                                       "Shipper": {
                                           "Reference1": f"{old_order}",
                                           "Reference2": "",
                                           "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                                           "PartyAddress": {
                                               "Line1": "Oman",
                                               "Line2": "",
                                               "Line3": "",
                                               "City": "Oman",
                                               "StateOrProvinceCode": "",
                                               "PostCode": "",
                                               "CountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                                               "Longitude": 0,
                                               "Latitude": 0,
                                               "BuildingNumber": None,
                                               "BuildingName": None,
                                               "Floor": None,
                                               "Apartment": None,
                                               "POBox": None,
                                               "Description": "alithemes.com product"
                                           },
                                           "Contact": {
                                               "Department": "",
                                               "PersonName": "alithemes.com store",
                                               "Title": "",
                                               "CompanyName": "alithemes.com",
                                               "PhoneNumber1": "1111111111",
                                               "PhoneNumber1Ext": "",
                                               "PhoneNumber2": "",
                                               "PhoneNumber2Ext": "",
                                               "FaxNumber": "",
                                               "CellPhone": "1111111111111",
                                               "EmailAddress": "mail@alithemes.com",
                                               "Type": ""
                                           }
                                       },
                                       "Consignee": {
                                           "Reference1": f"{Consignee_id}",
                                           "Reference2": f"{Consignee_email}",
                                           "AccountNumber": f"{Consignee_id}",
                                           "PartyAddress": {
                                               "Line1": f"{old_order.address.address}",
                                               "Line2": "",
                                               "Line3": "",
                                               "City": f"{old_order.address.City}",
                                               "StateOrProvinceCode": f"{old_order.address.state}",
                                               "PostCode": f"{old_order.address.post_code}",
                                               "CountryCode": f"{old_order.address.country}",
                                               "Longitude": 0,
                                               "Latitude": 0,
                                               "BuildingNumber": "",
                                               "BuildingName": "",
                                               "Floor": "",
                                               "Apartment": "",
                                               "POBox": None,
                                               "Description": "Please contact me when the shipment arrives"
                                           },
                                           "Contact": {
                                               "Department": "",
                                               "PersonName": f"{old_order.owner.first_name} {old_order.owner.last_name}",
                                               "Title": f"{old_order.owner.last_name}",
                                               "CompanyName": "",
                                               "PhoneNumber1": f"{old_order.address.phone}",
                                               "PhoneNumber1Ext": "",
                                               "PhoneNumber2": "",
                                               "PhoneNumber2Ext": "",
                                               "FaxNumber": "",
                                               "CellPhone": f"{old_order.address.phone}",
                                               "EmailAddress": f"{old_order.owner.email}",
                                               "Type": ""
                                           }
                                       },
                                       "ThirdParty": {
                                           "Reference1": "",
                                           "Reference2": "",
                                           "AccountNumber": "",
                                           "PartyAddress": {
                                               "Line1": "",
                                               "Line2": "",
                                               "Line3": "",
                                               "City": "",
                                               "StateOrProvinceCode": "",
                                               "PostCode": "",
                                               "CountryCode": "",
                                               "Longitude": 0,
                                               "Latitude": 0,
                                               "BuildingNumber": None,
                                               "BuildingName": None,
                                               "Floor": None,
                                               "Apartment": None,
                                               "POBox": None,
                                               "Description": None
                                           },
                                           "Contact": {
                                               "Department": "",
                                               "PersonName": "",
                                               "Title": "",
                                               "CompanyName": "",
                                               "PhoneNumber1": "",
                                               "PhoneNumber1Ext": "",
                                               "PhoneNumber2": "",
                                               "PhoneNumber2Ext": "",
                                               "FaxNumber": "",
                                               "CellPhone": "",
                                               "EmailAddress": "",
                                               "Type": ""
                                           }
                                       },
                                       "ShippingDateTime": str('/Date(' + str(time) + ')/'),
                                       "DueDate": str('/Date(' + str(time) + ')/'),
                                       "Comments": "",
                                       "PickupLocation": "",
                                       "OperationsInstructions": "",
                                       "AccountingInstrcutions": "",
                                       "Details": {
                                           "Dimensions": None,
                                           "ActualWeight": {
                                               "Unit": "KG",
                                               "Value": float(old_order.weight)
                                           },
                                           "ChargeableWeight": None,
                                           "DescriptionOfGoods": None,
                                           "GoodsOriginCountry": "IN",
                                           "NumberOfPieces": 1,
                                           "ProductGroup": product_group,
                                           "ProductType": product_type,
                                           "PaymentType": "P",
                                           "PaymentOptions": "",
                                           "CustomsValueAmount": None,
                                           "CashOnDeliveryAmount": None,
                                           "InsuranceAmount": None,
                                           "CashAdditionalAmount": None,
                                           "CashAdditionalAmountDescription": "",
                                           "CollectAmount": None,
                                           "Services": "",
                                           "Items": []
                                       },
                                       "Attachments": [],
                                       "ForeignHAWB": "",
                                       "TransportType ": 0,
                                       "PickupGUID": "",
                                       "Number": None,
                                       "ScheduledDelivery": None
                                   }
                               ],
                               "Transaction": None

                           }

                           url = 'https://ws.aramex.net/ShippingAPI.V2/Shipping/Service_1_0.svc/json/CreateShipments'
                           r = requests.post(url, json=data)
                           # print(type(r.content) )
                           soup = BeautifulSoup(r.content, 'html.parser')
                           # print(soup)
                           old_order.tracking_no = soup.id.string
                           old_order.rpt_cache = soup.labelurl.string

                       # delete available
                       # products_details = OrderItem.objects.all().filter(order=old_order)
                       # for pro in products_details:
                       #     product_order = Products.objects.get(
                       #         id=pro.product.id)
                       #     if product_order.available > 0:
                       #         product_order.available = product_order.available - pro.quantity
                       #         product_order.save()

                       old_order.ordered = True
                       old_order.order_status = "OnShipping"
                       old_order.payment_status = "Completed"
                       old_order.save()

                       # code for set supplier's balance
                       # obj_order_suppliers = OrderSupplier.objects.all().filter(order=old_orde)
                       # for obj_order_supplier in obj_order_suppliers:
                       #     supplier = Profile.objects.get(
                       #         id=obj_order_supplier.vendor.id)
                       #     supplier.blance = float(
                       #         supplier.blance) + float(obj_order_supplier.amount)
                       #     supplier.save()
                       try:

                           message = f"Your order has been successfully purchased, Order ID {old_order.id}."
                           notify_user_ticket(request, old_order.owner.email, message)
                       except:
                           pass
                       if "coupon_id" in request.session.keys():
                           del request.session["coupon_id"]
                       order_data = {
                           "order_id": old_order.id,
                           "order_status": old_order.order_status,
                           "payment_status": old_order.payment_status,
                           "ordered": old_order.ordered,
                           "tracking_no": old_order.tracking,

                       }

                       return JsonResponse(order_data, status=HTTP_201_CREATED, safe=False)

                   else:
                       messages.warning(
                           request, f"A technical problem has occurred, please contact technical support")
                       return JsonResponse('order_data Error', status=HTTP_201_CREATED, safe=False)
           else:
               messages.warning(
                   request, f"A technical problem has occurred, please contact technical support")
               return JsonResponse('order_data Error', status=HTTP_201_CREATED, safe=False)
       else:
           return JsonResponse('order_data Error', status=HTTP_400_BAD_REQUEST, safe=False)
    except Exception as e:

        return JsonResponse(f'order_data Error {e}', status=HTTP_400_BAD_REQUEST, safe=False)





