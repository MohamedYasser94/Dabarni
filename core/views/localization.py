from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse, translate_url
from django.utils import translation
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _, check_for_language
# Create your views here.
from django.views.i18n import LANGUAGE_QUERY_PARAMETER

from Dabarni.settings import LANGUAGE_SESSION_KEY
from core.forms.core import AdminCommonTranslateForm
from core.forms.localization import  AdminLanguageForm
from core.models.localization import Language
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import staff_only, authenticated_staff


#############Rosetta##########

@authenticated_staff
@staff_only
def AdminLanguageList(request):
    languages = Language.objects.all()
    language_form = AdminLanguageForm()
    if request.method == "POST":
        if language_form:
            name = request.POST.get('name')
            code = request.POST.get('code')
            image = request.FILES.get('image')
            status = 'Active'
            language_object = Language(name=name, code=code, image=image, status=status)
            language_object.save()
            messages.success(request, "Language Add Successfully", extra_tags='Language')
            return HttpResponseRedirect(reverse('core:AdminLanguageList'))
        else:
            messages.error(request, "Language Not Add", extra_tags='Language')
    context = {
        'languages': languages,
        'language_form': language_form,
        'current_page': _('Language'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/language/admin.html', context)




@authenticated_staff
@staff_only
def AdminLanguageUpdate(request, slug):
    # Use get_object_or_404 for better error handling
    language = get_object_or_404(Language, slug=slug)

    if request.method == "POST":
        # Pass the instance to update the existing object
        form = AdminLanguageForm(request.POST, request.FILES, instance=language)
        if form.is_valid():
            form.save()  # This single line saves all the changes to the model
            messages.success(request, _("Language updated successfully."), extra_tags='Language')
            return HttpResponseRedirect(reverse('core:AdminLanguageList'))
        else:
            # If the form is not valid, it will be re-rendered with errors
            messages.error(request, _("Could not update language. Please check the errors below."), extra_tags='Language')
    else:
        # For a GET request, create a form instance with the language data
        form = AdminLanguageForm(instance=language)

    context = {
        'language': language,
        'form': form,  # Pass the form object to the template
        'current_page': _('Detail'),
        'prev_Page': _('Language'),
        'prev_Page_link': reverse_lazy('core:AdminLanguageList')
    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/language/update.html', context)

def AdminLanguageDelete(request, slug):
    if request.method == "POST":
        try:
            language_object = Language.objects.get(slug=slug)
            language_object.delete()
            messages.success(request, "Language Deleted Successfully", extra_tags='Language')
            return HttpResponseRedirect(reverse('core:AdminLanguageList'))
        except Exception as e:
            print(e)
            messages.error(request, "Language Not Deleted", extra_tags='Language')
            return HttpResponseRedirect(reverse('core:AdminLanguageList'))

def select_language(request, code):
    try:
        cur_language = code
        lasturl = request.META.get('HTTP_REFERER')
        print(code, '1')
        lang = Language.objects.get(code=code)
        # user_setting = UserSetting.objects.get(user=request.user)
        # user_setting.lang = lang
        # user_setting.save()
        translation.activate(code)

        request.session[LANGUAGE_SESSION_KEY] = 'lang'
        return set_language(request)


    except Exception as e:

        return redirect(request.META['HTTP_REFERER'])

    # if request.user.is_authenticated and request.method == 'POST':  # check post
    #     cur_language = code
    #     lasturl = request.META.get('HTTP_REFERER')
    #     print(code,'1')
    #     lang = Language.objects.get(code=cur_language)
    #     # user_setting = UserSetting.objects.get(user=request.user)
    #     # user_setting.lang = lang
    #     # user_setting.save()
    #     translation.activate(lang)
    #     request.session[LANGUAGE_SESSION_KEY] = lang
    #     # return HttpResponse(lang)
    #     return redirect(request.META['HTTP_REFERER'])
    # else:
    #         cur_language = translation.get_language()
    #         lasturl = request.META.get('HTTP_REFERER')
    #         lang = code
    #         print(lang,2)
    #         translation.activate(lang)
    #         print(lasturl)
    #         # request.session.get
    #
    #         request.session[LANGUAGE_SESSION_KEY] = lang
    #         # return HttpResponse(lang)
    #         return HttpResponseRedirect(lasturl)


def set_language(request):
    """
    Redirect to a given URL while setting the chosen language in the session
    (if enabled) and in a cookie. The URL and the language code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.
    """
    next_url = request.POST.get("next", request.GET.get("next"))
    if (
            next_url or request.accepts("text/html")
    ) and not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = request.META.get("HTTP_REFERER")
        if not url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
        ):
            next_url = "/"
    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=204)
    if request.method == "POST":
        lang_code = request.POST.get(LANGUAGE_QUERY_PARAMETER)
        if lang_code and check_for_language(lang_code):
            if next_url:
                next_trans = translate_url(next_url, lang_code)
                if next_trans != next_url:
                    response = HttpResponseRedirect(next_trans)
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                lang_code,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )
    return response


