import random
import string
from io import BytesIO
from imagekit import ImageSpec, processors
import jwt
from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import models
from rest_framework import authentication, exceptions

User = get_user_model()

class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'UserToken'

    def authenticate(self, request):
        """
        The `authenticate` method is called on every request regardless of
        whether the endpoint requires authentication.

        `authenticate` has two possible return values:

        1) `None` - We return `None` if we do not wish to authenticate. Usually
                    this means we know authentication will fail. An example of
                    this is when the request does not include a token in the
                    headers.

        2) `(user, token)` - We return a user/token combination when
                             authentication is successful.

                            If neither case is met, that means there's an error
                            and we do not return anything.
                            We simple raise the `AuthenticationFailed`
                            exception and let Django REST Framework
                            handle the rest.
        """
        request.user = None

        # `auth_header` should be an array with two elements: 1) the title of
        # the authentication header (in this case, "UserToken") and 2) the JWT
        # that we should authenticate against.
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Invalid token header. No credentials provided. Do not attempt to
            # authenticate.
            return None

        elif len(auth_header) > 2:
            # Invalid token header. The UserToken string should not contain spaces. Do
            # not attempt to authenticate.
            return None

        # The JWT library we're using can't handle the `byte` type, which is
        # commonly used by standard libraries in Python 3. To get around this,
        # we simply have to decode `prefix` and `token`. This does not make for
        # clean code, but it is a good decision because we would get an error
        # if we didn't decode these values.
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # The auth header prefix is not what we expected. Do not attempt to
            # authenticate.
            return None

        # By now, we are sure there is a *chance* that authentication will
        # succeed. We delegate the actual credentials authentication to the
        # method below.
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except:
            msg = 'Invalid authentication. Could not decode token.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)


def RandomEmailAddressGenerator(request):
    validchars = string.ascii_letters + string.digits
    loginlen = random.randint(4, 15)
    login = ''
    for i in range(loginlen):
        pos=random.randint(0, len(validchars)-1)
        login=login+validchars[pos]
    if login[0].isnumeric():
        pos=random.randint(0, len(validchars)-10)
        login=validchars[pos]+login
    servers=['@gmail', '@yahoo', '@hotmail', '@outlook', '@aol', '@yandex', '@mail', '@protonmail',
             '@zoho', '@gmx', '@icloud', '@inbox', '@gmx', '@yopmail', '@mailinator', '@gmx']
    servpos=random.randint(0, len(servers)-1)
    email=login+servers[servpos]
    tlds=['.com','.in','.co.in','.org','.net','.xyz','.info','.co.uk','.co','.us','.biz','.mobi','.tv','.ws','.name','.cc','.de','.jp','.be','.at',
          '.co.nz','.net.nz','.org.uk',
          '.me.uk','.cn','.com.cn','.org.cn','.net.cn','.tw','.com.tw','.org.tw','.idv.tw','.jobs','.eu','.fm','.ms','.nu','.tc','.tk','.vg']
    tldpos=random.randint(0, len(tlds)-1)
    email=email+tlds[tldpos]
    return email


def RandomPasswordGenerator():
    """Generates a random password string."""
    valid_chars = string.ascii_letters + string.digits
    length = random.randint(8, 15)
    return ''.join(random.choice(valid_chars) for _ in range(length))

def RandomUsernameGenerator(request):
    validchars = string.ascii_letters + string.digits
    usernamelen = random.randint(4, 15)
    username = ''
    for i in range(usernamelen):
        pos=random.randint(0, len(validchars)-1)
        username=username+validchars[pos]
    return username

def RandomNameGenerator(request):
    validchars = string.ascii_letters
    namelen = random.randint(4, 15)
    name = ''
    for i in range(namelen):
        pos=random.randint(0, len(validchars)-1)
        name=name+validchars[pos]
    return name

def RandomEgyptPhoneGenerator(request):
    validators = string.digits
    provider = ['010', '011', '012', '015', '016', '017', '018', '019']
    mobile_number1 = random.randint(1000, 9999)
    mobile_number2 = random.randint(888, 1111)
    for i in provider:
        phone = i + str(mobile_number1) + str(mobile_number2)

    return phone


def compress_image(image):
  """
  Compresses an image to a target size (around 100kb) using Pillow.

  Args:
      image: The uploaded image object.

  Returns:
      A compressed image as a Django File object.
  """
  im = Image.open(image)
  # Start with high quality, adjust down if needed
  quality = 80
  output = BytesIO()
  while True:
      im.save(output, format='JPEG', quality=quality)
      content = output.getvalue()
      if len(content) <= 102400:  # 100kb in bytes
          return content
      quality -= 10
      # Adjust quality until target size is reached or minimum is hit
      if quality < 50:
          return content  # Return even if larger than 100kb


class WEBPImageField(models.ImageField):
    def save(self, name, content, save=True):
        """
        Converts uploaded image to WebP format before saving.
        """
        if content is None:
            return

        # Open image using Pillow
        image = Image.open(content)
        webp_buffer = BytesIO()
        image.save(webp_buffer, format='WEBP')

        # Create a ContentFile object with WebP data
        webp_content = ContentFile(webp_buffer.getvalue())
        webp_content.name = f'{name}.webp'  # Append .webp extension

        # Save the WebP content
        super().save(name, webp_content, save=save)


class CompressedImageSpec(ImageSpec):
  """
  ImageSpec for compressing uploaded images.
  """
  format = 'JPEG'
  processors = [processors.ResizeToFill(1280, 720)]  # Optional resize
  options = {'quality': 80}  # Initial quality

  def get_processors(self, *args, **kwargs):
    options = super().get_options(*args, **kwargs)
    options['quality'] = min(options['quality'], 50)  # Minimum quality
    return super().get_processors(*args, options=options, **kwargs)


def current_language(request):
    """
    Get the current language from the request headers.
    """
    return request.headers.get('Accept-Language', 'en')