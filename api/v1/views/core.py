from django.http import JsonResponse

from api.v1.serializers.core import *
from core.models.core import *


def ApiConfigSetting(request):
    try:
        # get_or_create is safer to ensure a config object always exists
        config, created = ConfigSetting.objects.get_or_create(id=1)

        # Use the new serializer
        config_serializer = ConfigSettingSerializer(config, context={'request': request})

        success = True
        message = "Success"
        config_data = config_serializer.data
        data = {'error': not success, 'data': config_data,
                'message': message}  # Using 'error' key as per Flutter API class

        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"Error: {e}"
        data = {'error': not success, 'data': {}, 'message': message}
        return JsonResponse(data, safe=False)


