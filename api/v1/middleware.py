from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.utils.deprecation import MiddlewareMixin
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.conf import settings

class CheckTokenBlacklistMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token_str = auth_header.split(' ')[1]
            try:
                
                UntypedToken(token_str)              
                token = BlacklistedToken.objects.filter(token__token=token_str).first()
                if token:
                    return Response({"error": "Token is blacklisted. Please login again."}, status=status.HTTP_401_UNAUTHORIZED)
            except TokenError:
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_401_UNAUTHORIZED)
        return None
