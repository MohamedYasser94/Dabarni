import json

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from api.v1.serializers.common import FrontCommonMediaFilesSerializer
from core.models.core import CommonMediaFiles
from core.models.localization import Currency, Language
from helper.modelHelper import SAUDI_CITIES_BY_GOVERNORATE
from user.models import UserAddress


################### Search API ############################
@csrf_exempt
def AdminApiSearch(request):
    print('AdminApiSearch request', request.POST , request.method)
    if request.method == 'POST':

        search = request.POST.get('search')
        print('AdminApiSearch', search)

        data = {
            'success': True,
            'treatments': [],
            'persons': [],
            'status': '200'
        }
        return JsonResponse(data, safe=False)

    else:
        data = {
            'success': False,
            'treatments': [],

            'persons': [],
            'status': '400'
        }
        return JsonResponse(data, safe=False)


@csrf_exempt
def ApiCurrencyList(request):
    """
    This view provides the single, default currency details in the format
    expected by the Flutter application.

    It finds the currency marked as 'Active' in the 'default' field.
    """
    if request.method == 'GET':
        try:
            # Fetch the single currency that is set as the default for the app.
            # The model uses `unique=True` on the `default` field to ensure only one can be 'Active'.
            default_currency = Currency.objects.filter(default='Active')
            if not default_currency.exists():
                default_currency = Currency(
                    symbol='$',
                    position='left',
                    currency_code='USD',
                    exchange='USD/USD',

                    default='Active'
                )


            # Construct the response dictionary to match the Flutter app's structure
            response_data = {
                'currency': {
                    'symbol': default_currency.symbol,
                    'position': default_currency.position,
                    'code': default_currency.currency_code,
                }
            }
            return JsonResponse(response_data, status=200)

        except Currency.DoesNotExist:
            # This error occurs if no currency is set as the default
            return JsonResponse({
                'error': 'No default currency has been configured in the system.'
            }, status=404)

        except Currency.MultipleObjectsReturned:
            # This error occurs if more than one currency is marked as default,
            # which shouldn't happen if `unique=True` is set on the model field.
            return JsonResponse({
                'error': 'Configuration error: Multiple default currencies found. Please contact support.'
            }, status=500)

        except Exception as e:
            # Catch any other unexpected errors
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method. Only GET is allowed.'}, status=405)


@csrf_exempt
def ApiLanguageList(request):
    """
    This view provides the details for a specific language based on its code.
    The language code is passed as a GET parameter.
    If no code is provided, it returns the default language.
    """
    if request.method != 'GET':
        return JsonResponse({'error': True, 'message': 'Invalid request method.'}, status=405)

    language_code = request.GET.get('language_code', None)

    try:
        if language_code:
            # Fetch the language specified by the code
            language_obj = Language.objects.get(code=language_code, status='Active')
        else:
            # If no code is provided, fetch the default language
            language_obj = Language.objects.get(default='Active', status='Active')

    except Language.DoesNotExist:
        return JsonResponse({'error': True, 'message': 'Language not found.'}, status=404)
    except Language.MultipleObjectsReturned:
        # This can happen if more than one language is marked as default.
        # The model's save method should prevent this, but this is a safeguard.
        return JsonResponse({'error': True, 'message': 'Configuration error: Multiple default languages found.'},
                            status=500)
    except Exception as e:
        return JsonResponse({'error': True, 'message': f'An unexpected error occurred: {str(e)}'}, status=500)

    # Construct the response data to match the Flutter app's expectations
    response_data = {
        'id': language_obj.id,
        'slug': language_obj.slug,
        'default': language_obj.default == 'Active',  # Convert 'Active'/'Inactive to a boolean
        'status': language_obj.status == 'Active',  # Convert 'Active'/'Inactive' to a boolean
        'direction': language_obj.direction,  # Assuming this
        'code': language_obj.code,
        'country_code': language_obj.country_code,
        'name': language_obj.name,
        'name_in_english': language_obj.name_in_english,
        'image': request.build_absolute_uri(language_obj.image.url) if language_obj.image else '',
        'file_name': language_obj.get_translations(),  # Get JSON content from the file
        'rtl': language_obj.direction == 'rtl',  # Convert 'rtl'/'ltr' to a boolean
        'translations': language_obj.translations # Assuming this method returns a dict of translations

    }

    # Wrap the data in 'data' key as seen in other API responses
    return JsonResponse({'error': False, 'data': response_data})


@api_view(['GET'])
@permission_classes([AllowAny])
def ApiLanguagePack(request, lang_code):
    """
    Returns the full JSON translation file for a given language code.
    e.g., /api/v1/language-pack/ar/
    """
    try:
        language = Language.objects.get(code=lang_code, status='Active')

        # FIX: Return the 'translations' JSONField, not the old 'file_name' field.
        return Response(language.translations, status=status.HTTP_200_OK)

    except Language.DoesNotExist:
        return Response({"error": f"Language pack for '{lang_code}' not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def ApiTranslateString(request):
    """
    This view receives a JSON object with a language code and a JSON string
    of key-value pairs. It translates the keys and returns a full JSON
    object of translated strings.

    Expected request body format:
    {
        "lang": "ar",
        "strings": "{\"Welcome\":\"Welcome\",\"Enter your email\":\"Enter your email\"}"
    }

    Successful response format:
    {
        "strings": {
            "Welcome": "أهلاً بك",
            "Enter your email": "أدخل بريدك الإلكتروني"
        }
    }
    """
    try:
        # 1. Get data from the POST request body. DRF automatically parses JSON.
        data = request.data
        language_code = data.get('lang')

        # The 'strings' value is a stringified JSON, so we need to parse it.
        strings_to_translate_json = data.get('strings')

        if not language_code or not strings_to_translate_json:
            return JsonResponse({
                'error': True,
                'message': 'Request body must contain "lang" and "strings" keys.'
            }, status=400)

        # 2. Parse the inner JSON string into a Python dictionary
        default_strings_dict = json.loads(strings_to_translate_json)
        if not isinstance(default_strings_dict, dict):
            raise ValueError("The 'strings' key must contain a valid JSON object string.")

    except (KeyError, json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'error': True, 'message': f'Invalid request format: {str(e)}'}, status=400)

    try:
        # 3. Fetch all translations for the target language once.
        # This assumes you have a method that returns a dict like {'Hello': 'مرحبا'}.
        # If Language model doesn't exist, this will raise Language.DoesNotExist.
        language_obj = Language.objects.get(code=language_code, status='Active')
        all_translations_for_lang = language_obj.get_translations()  # Assuming this method exists

        translated_strings = {}
        # 4. Iterate through the dictionary from Flutter and build the translated dictionary
        for key, default_value in default_strings_dict.items():
            # Use the translation if it exists, otherwise fall back to the original string
            translated_strings[key] = all_translations_for_lang.get(key, default_value)

        # 5. Return the response in the format Flutter expects
        return JsonResponse({'strings': translated_strings}, status=200)

    except Language.DoesNotExist:
        # If the language is not supported, just return the default strings
        return JsonResponse({'strings': default_strings_dict}, status=200)
    except Exception as e:
        return JsonResponse({'error': True, 'message': f'An unexpected server error occurred: {str(e)}'}, status=500)

##########################      Blog Categories Admin            ################################
class CommonMediaFilesList(RetrieveAPIView):
    queryset = CommonMediaFiles.objects.all()
    serializer_class = FrontCommonMediaFilesSerializer
    lookup_field = 'id'

    def get(self, request, id):
        post = self.get_object(id)
        serializer = FrontCommonMediaFilesSerializer(post)
        return Response({
            'result': serializer.data,
            'message': 'success'
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saudi_governorates(request):
    """
    Returns a list of Saudi Arabian governorates.
    """
    # Assuming Governorates_List is a list of tuples like (db_value, display_name)
    governorates = [{'id': choice[0], 'name': choice[1]} for choice in UserAddress.governorates]
    return Response(governorates, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saudi_cities(request, governorate_id):
    """
    Returns a list of cities for a given Saudi governorate.
    """
    cities = SAUDI_CITIES_BY_GOVERNORATE.get(governorate_id, [])
    city_list = [{'id': city, 'name': city} for city in cities]
    return Response(city_list, status=status.HTTP_200_OK)



