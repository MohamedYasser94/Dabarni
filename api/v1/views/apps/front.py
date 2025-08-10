from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



from api.v1.serializers.app.front import *
from apps.front.models.models import *


@csrf_exempt
def ApiHomeSlider(request):
    """
    This view provides a list of banners in a format that matches the Flutter application's Banner model.
    """
    try:
        slider_list = SliderItem.objects.filter(status='Active').order_by('order')

        # Use the new serializer to format the data correctly
        slider_serializer = SliderItemSerializer(slider_list, many=True, context={'request': request})

        banner_data = slider_serializer.data
        data = {'success': True, 'data': banner_data, 'message': "Success"}
    except Exception as e:
        data = {'success': False, 'data': [], 'message': f"Error: {str(e)}"}

    return JsonResponse(data, safe=False)



@csrf_exempt
def ApiFrontBanner(request):
    try:
        banner = BannerItem.objects.filter(status = 'Active')
        banner_serializer = BannerSerializer(banner, many=True, context={'request': request})
        success = True
        message = f"Success "
        banner_data = banner_serializer.data
        data = {'success': success, 'data': banner_data, 'message': message, }
    except Exception as e:
        success = True
        message = f"Success "
        catalog_data = {'data': [], }
        data = {'success': success, 'data': catalog_data, 'message': message, }
    return JsonResponse(data, safe=False)


@csrf_exempt
def ApiFaq(request):
    """
    This view provides a list of FAQs in a format that matches the Flutter application's Faq model.
    """
    try:
        faq_list = Faq.objects.filter(status='Active').order_by('order')
        faq_serializer = FaqSerializer(faq_list, many=True, context={'request': request})
        success = True
        message = "Success"
        faq_data = faq_serializer.data
        data = {'success': success, 'data': faq_data, 'message': message}
    except Exception as e:
        success = False
        message = f"Error: {str(e)}"
        data = {'success': success, 'data': [], 'message': message}
    return JsonResponse(data, safe=False)
@csrf_exempt
def ApiPrivacyPolicy(request):
    """
    This view now provides a list of static pages (like Privacy Policy and Terms & Conditions)
    in a format that matches the Flutter application's PolicyPage model.
    """
    try:
        pagelist_data = []

        # Fetch the latest active Privacy Policy
        privacy_policy = PrivacyPolicy.objects.filter(status='Active').last()
        if privacy_policy:
            # Assuming the model has 'title' and 'description' fields
            pagelist_data.append({
                'title': getattr(privacy_policy, 'title', 'Privacy Policy'),
                'description': getattr(privacy_policy, 'description', 'No content available.')
            })

        # Fetch the latest active Terms and Conditions
        terms_and_conditions = TermsAndConditions.objects.filter(status='Active').last()
        if terms_and_conditions:
            # Assuming the model has 'title' and 'description' fields
            pagelist_data.append({
                'title': getattr(terms_and_conditions, 'title', 'Terms & Conditions'),
                'description': getattr(terms_and_conditions, 'description', 'No content available.')
            })

        # Check if any pages were found and create the response
        if pagelist_data:
            response_data = {
                'pagelist': pagelist_data,
                'ResponseCode': '200',
                'Result': 'True',
                'ResponseMsg': 'SUCCESS',
            }
        else:
            response_data = {
                'pagelist': [],
                'ResponseCode': '404',
                'Result': 'False',
                'ResponseMsg': 'No pages found',
            }
    except Exception as e:
        # Handle potential exceptions during database query
        response_data = {
            'pagelist': [],
            'ResponseCode': '500',
            'Result': 'False',
            'ResponseMsg': f'An error occurred: {str(e)}',
        }
    return JsonResponse(response_data)

@csrf_exempt
def TermsAndConditionsView(request):
    try:
        terms_and_conditions = TermsAndConditions.objects.filter(status='Active').last()
        if terms_and_conditions:
            terms_and_conditions_serializer = TermsAndConditionsSerializer(terms_and_conditions, context={'request': request})
            success = True
            message = f"Success "
            terms_and_conditions_data = terms_and_conditions_serializer.data
            data = {'success': success, 'data': terms_and_conditions_data, 'message': message, }
        else:
            success = False
            message = f"Terms and Conditions not found"
            data = {'success': success, 'data': [], 'message': message, }
    except Exception as e:
        success = False
        message = f"Error: {str(e)}"
        data = {'success': success, 'data': [], 'message': message, }
    return JsonResponse(data, safe=False)
