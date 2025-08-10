import requests


from Dabarni import settings


def getLocation(request):
    abstractApi_key = settings.ABSTRACT_API_KEY

    url = "https://ipgeolocation.abstractapi.com/v1/?api_key=" + abstractApi_key
    ip = request.META.get('REMOTE_ADDR')

    response = requests.get(url+"&ip_address="+ip)
    data = response.json()

    return data





