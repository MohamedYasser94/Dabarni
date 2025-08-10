from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse, translate_url
from django.utils import timezone
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _, check_for_language
# Create your views here.
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.i18n import LANGUAGE_QUERY_PARAMETER

from Dabarni.settings import LANGUAGE_SESSION_KEY
from core.forms.core import AdminCommonTranslateForm
from core.forms.localization import AdminCountryForm, AdminCurrencyForm, AdminLanguageForm, AdminCityForm, \
    AdminAreaForm, AdminGovernoratesForm
from core.models.localization import Country, Governorates, City, Area, Language, Currency
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import superuser_only, staff_only, authenticated_staff


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


############Currency############

@authenticated_staff
@staff_only
def AdminCurrencyList(request):
    currencies = Currency.objects.all()
    currency_form = AdminCurrencyForm()
    if request.method == "POST":
        if currency_form:
            name = request.POST.get('name')
            currency_code = request.POST.get('currency_code')
            default = request.POST.get('default')
            status = request.POST.get('status')

            try:
                currency_object = Currency.objects.get(currency_code=currency_code)
                messages.error(request, "Currency Code Already Exist", extra_tags='Currency')
                return HttpResponseRedirect(reverse('core:AdminCurrencyList'))
            except:
                pass
            try:
                currency_object = Currency.objects.get(name=name)
                messages.error(request, "Currency Name Already Exist", extra_tags='Currency')
                return HttpResponseRedirect(reverse('core:AdminCurrencyList'))
            except:
                pass

            if default == 'Active':
                currency = Currency.objects.filter(default='Active')
                if currency:
                    messages.error(request, "Default Currency Already Exist", extra_tags='Currency')
                    return HttpResponseRedirect(reverse('core:AdminCurrencyList'))
                else:
                    currency_object = Currency(name=name, currency_code=currency_code, default=default, status=status)
                    currency_object.save()
                    messages.success(request, "Currency Add Successfully", extra_tags='Currency')
                    return HttpResponseRedirect(reverse('core:AdminCurrencyList'))
            else:
                currency_object = Currency(name=name, currency_code=currency_code, default=default, status=status)
                currency_object.save()
                messages.success(request, "Currency Add Successfully", extra_tags='Currency')
                return HttpResponseRedirect(reverse('core:AdminCurrencyList'))

        else:
            messages.error(request, "Currency Not Add", extra_tags='Currency')
    context = {
        'currencies': currencies,
        'currency_form': currency_form,
        'current_page': _('Currency'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/currency/admin.html', context)


@authenticated_staff
@staff_only
def AdminCurrencyDetails(request, slug):
    currency = Currency.objects.get(slug=slug)
    context = {
        'currency': currency,
        'current_page': _('Detail'),
        'prev_Page': _('Currency'),
        'prev_Page_link': reverse_lazy('core:AdminCurrencyList')

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/currency/detail.html', context)


@authenticated_staff
@staff_only
def AdminCurrencyCreate(request):
    currencies = Currency.objects.all()
    if request.method == "POST":
        currency_form = AdminCurrencyForm(request.POST or None, request.FILES or None)
        if currency_form.is_valid():
            name = request.POST.get('name')
            name_ar = request.POST.get('name_ar')
            code = request.POST.get('code')
            symbol = request.POST.get('symbol')
            status = request.POST.get('status')
            currency_form = Currency(name=name, name_ar=name_ar, code=code, symbol=symbol, status=status)
            currency_form.save()
            messages.success(request, _("Currency Add Successfully"), extra_tags='Currency')
            return HttpResponseRedirect(reverse('core:AdminCurrencyList'))
        else:
            messages.error(request, _("Currency Not Add , Please Try Again"), extra_tags='Currency')

    else:
        currency_form = AdminCurrencyForm()
        context = {
            'currencies': currencies,
            'currency_form': currency_form,
            'current_page': _('Create'),
            'prev_Page': _('Currency'),
            'prev_Page_link': reverse_lazy('core:AdminCurrencyList')

        }
        return render(request, f'{BACKEND_TEMPLATES}/localization/currency/add.html', context)
    context = {
        'currencies': currencies,
        'currency_form': currency_form,
        'current_page': _('Create'),
        'prev_Page': _('Currency'),
        'prev_Page_link': reverse_lazy('core:AdminCurrencyList')

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/currency/add.html', context)


@authenticated_staff
@staff_only
def AdminCurrencyUpdate(request, slug):
    currency = Currency.objects.get(slug=slug)
    if request.method == "POST":
        currency_form = AdminCurrencyForm(request.POST or None, request.FILES or None)
        if currency_form.is_valid():
            name = request.POST.get('name')
            name_ar = request.POST.get('name_ar')
            code = request.POST.get('code')
            symbol = request.POST.get('symbol')
            status = request.POST.get('status')
            currency_form = Currency.objects.get(slug=slug)
            currency_form.name = name
            currency_form.name_ar = name_ar
            currency_form.code = code
            currency_form.symbol = symbol
            currency_form.status = status
            currency_form.save()
            messages.success(request, _("Currency Update Successfully"), extra_tags='Currency')
            return HttpResponseRedirect(reverse('core:AdminCurrencyList'))
        else:
            messages.error(request, _("Currency Not Update , Please Try Again"), extra_tags='Currency')

    else:
        currency_form = AdminCurrencyForm()
        context = {
            'currency': currency,
            'currency_form': currency_form,
            'current_page': _('Update'),
            'prev_Page': _('Currency'),
            'prev_Page_link': reverse_lazy('core:AdminCurrencyList')

        }
        return render(request, f'{BACKEND_TEMPLATES}/localization/currency/update.html', context)
    context = {
        'currency': currency,
        'currency_form': currency_form,
        'current_page': _('Update'),
        'prev_Page': _('Currency'),
        'prev_Page_link': reverse_lazy('core:AdminCurrencyList')

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/currency/update.html', context)


@authenticated_staff
@staff_only
def AdminCurrencyDelete(request, slug):
    if request.method == "POST":
        try:
            currency_object = Currency.objects.get(slug=slug)
            currency_object.delete()
            messages.success(request, "Currency Deleted Successfully", extra_tags='Currency')
            return HttpResponseRedirect(reverse('core:AdminCurrencyList'))
        except Exception as e:
            print(e)
            messages.error(request, "Currency Not Deleted", extra_tags='Currency')
            return HttpResponseRedirect(reverse('core:AdminCurrencyList'))


############Country############

@authenticated_staff
@staff_only
def AdminCountryList(request):
    countries = Country.objects.all()
    country_form = AdminCountryForm()
    if request.method == "POST":
        if country_form:
            name = request.POST.get('name')
            capital = request.POST.get('capital')
            nationality = request.POST.get('national')
            calling_code = request.POST.get('calling_code')
            flag_emoji = request.POST.get('flag_emoji')
            flag_svg = request.POST.get('flag_svg')
            flag_svg_path = request.POST.get('flag_svg_path')
            image = request.FILES.get('image')
            status = request.POST.get('status')
            country_object = Country(
                name=name,capital=capital,nationality=nationality,calling_code=calling_code,flag_emoji=flag_emoji,
                flag_svg=flag_svg,flag_svg_path=flag_svg_path,image=image,status=status)

            country_object.save()
            messages.success(request, "Country Add Successfully", extra_tags='Country')
            return HttpResponseRedirect(reverse('core:AdminCountryList'))
        else:
            messages.error(request, "Country Not Add", extra_tags='Country')

    context = {
        'countries': countries,
        'country_form': country_form,
        'current_page': _('Country'),
    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/country/admin.html', context)


def AdminCountryDetails(request, slug):
    country = Country.objects.get(slug=slug)
    context = {
        'country': country,
        'current_page': _('Detail'),
        'prev_Page': _('Country'),
        'prev_Page_link': reverse_lazy('core:AdminCountryListView')

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/country/detail.html', context)


def AdminCountryUpdate(request, slug):
    country = Country.objects.get(slug=slug)
    if request.method == "POST":
        country_form = AdminCountryForm(request.POST or None, request.FILES or None)
        if country_form.is_valid():
            name = request.POST.get('name')
            image = request.FILES.get('image')
            status = request.POST.get('status')

            country_form = Country.objects.get(slug=slug)
            country_form.name = name
            if image:
                country_form.image = image
            else:
                country_form.image = country_form.image
            country_form.status = status
            country_form.save()
            messages.success(request, _("Country Update Successfully"), extra_tags='Country')
            return HttpResponseRedirect(reverse('core:AdminCountryList'))
        else:
            messages.error(request, _("Country Not Update , Please Try Again"), extra_tags='Country')

    else:
        country_form = AdminCountryForm()
        context = {
            'country': country,
            'country_form': country_form,
            'current_page': _('Update'),
            'prev_Page': _('Country'),
            'prev_Page_link': reverse_lazy('core:AdminCountryList')

        }
        return render(request, f'{BACKEND_TEMPLATES}/localization/country/update.html', context)
    context = {
        'country': country,
        'country_form': country_form,
        'current_page': _('Update'),
        'prev_Page': _('Country'),
        'prev_Page_link': reverse_lazy('core:AdminCountryList')

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/country/update.html', context)


@authenticated_staff
@staff_only
def AdminCountryDelete(request, slug):
    if request.method == "POST":
        try:
            country_object = Country.objects.get(slug=slug)
            country_object.delete()
            messages.success(request, "Country Deleted Successfully", extra_tags='Country')
            return HttpResponseRedirect(reverse('core:AdminCountryList'))
        except Exception as e:
            print(e)
            messages.error(request, "Country Not Deleted", extra_tags='Country')
            return HttpResponseRedirect(reverse('core:AdminCountryList'))


####################Governorates#################
@authenticated_staff
@staff_only
def AdminGovernoratesList(request, slug):
    country = Country.objects.get(slug=slug)
    governorates = Governorates.objects.filter(country=country)
    governorates_form = AdminGovernoratesForm()
    if request.method == "POST":
        if governorates_form:
            name = request.POST.get('name')
            status = request.POST.get('status')
            governorates_object = Governorates(country=country, name=name, status=status)
            governorates_object.save()
            messages.success(request, "Governorates Add Successfully", extra_tags='Governorates')
            return HttpResponseRedirect(reverse('core:AdminGovernoratesList', kwargs={"slug": country.slug}))
        else:
            messages.error(request, "Governorates Not Add", extra_tags='Governorates')

    context = {
        'country': country,
        'governorates': governorates,
        'governorates_form': governorates_form,
        'current_page': _('Governorates'),
        'prev_Page': _('Country'),
        'prev_Page_link': reverse_lazy('core:AdminCountryList', )

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/governorate/admin.html', context)


@authenticated_staff
@staff_only
def GovernoratesUpdate(request, slug, g_slug):
    country = Country.objects.get(slug=slug)
    governorates = Governorates.objects.get(slug=g_slug)
    if request.method == "POST":
        governorates_form = AdminGovernoratesForm(request.POST or None, request.FILES or None)
        name = request.POST.get('name')
        status = request.POST.get('status')

        if governorates_form:
            governorates_object = Governorates.objects.get(slug=g_slug)
            governorates_object.name = name
            governorates_object.status = status
            governorates_object.save()
            messages.success(request, "Governorates Update Successfully", extra_tags='Governorates')
            return HttpResponseRedirect(reverse('core:AdminGovernoratesList', kwargs={"slug": country.slug}))
        else:
            messages.error(request, "Governorates Update Not Update", extra_tags='Governorates')
    context = {
        'country': country,
        'governorates': governorates,
        'governorates_form': AdminGovernoratesForm(),
        'current_page': _('Update'),
        'prev_Page': _('Governorates'),
        'prev_Page_link': reverse_lazy('core:AdminGovernoratesList', kwargs={'slug': slug})
    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/governorate/update.html', context)


@authenticated_staff
@staff_only
def GovernoratesDelete(request, slug, g_slug):
    country = Country.objects.get(slug=slug)
    if request.method == "POST":
        try:
            country = Country.objects.get(slug=slug)
            governorates_object = Governorates.objects.get(slug=g_slug)
            governorates_object.delete()
            messages.success(request, "Governorates Deleted Successfully", extra_tags='Governorates')
            return HttpResponseRedirect(reverse('core:AdminGovernoratesList', kwargs={"slug": country.slug}))
        except:
            messages.error(request, "Error", extra_tags='Governorates')
            return HttpResponseRedirect(reverse('core:AdminGovernoratesList', kwargs={"slug": country.slug}))


##################     CIty    ##############


@authenticated_staff
@staff_only
def AdminCityList(request, slug):
    governorate = Governorates.objects.get(slug=slug)
    cities = City.objects.filter(governorates=governorate)
    city_form = AdminCityForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if city_form:
            name = request.POST.get('name')
            status = request.POST.get('status')
            city_object = City(governorates=governorate, name=name, status=status)
            city_object.save()
            messages.success(request, "City Add Successfully", extra_tags='City')
            return HttpResponseRedirect(reverse('core:AdminCityList', kwargs={"slug": governorate.slug}))
        else:
            messages.error(request, "City Not Add", extra_tags='City')

    context = {

        'governorate': governorate,
        'cities': cities,
        'city_form': city_form,
        'current_page': _('Cities'),
        'prev_Page': _('Governorates'),
        'prev_Page_link': reverse_lazy('core:AdminGovernoratesList', kwargs={'slug': slug})
    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/city/admin.html', context)


@authenticated_staff
@staff_only
def AdminCityUpdate(request, slug, c_slug):
    governorate = Governorates.objects.get(slug=slug)
    cities = City.objects.get(slug=c_slug)

    if request.method == "POST":

        governorate = Governorates.objects.get(slug=slug)
        city_form = AdminCityForm(request.POST or None, request.FILES or None)

        if city_form.is_valid():
            name = request.POST.get('name')
            if city_form:
                city_form = City.objects.get(slug=c_slug)
                city_form.name = name
                city_form.save()
                messages.success(request, "City Update Successfully", extra_tags='City')
                return HttpResponseRedirect(reverse('core:AdminCityList', kwargs={"slug": slug}))
        else:
            messages.error(request, "City Not Update", extra_tags='City')
    else:
        city_form = AdminCityForm()

        context = {
            'city': cities,
            'governorates': governorate,
            'city_form': city_form,
            'current_page': _('Update'),
            'prev_Page': _('Governorates'),
            'prev_Page_link': reverse_lazy('core:AdminCityList', kwargs={'slug': slug})

        }
        return render(request, f'{BACKEND_TEMPLATES}/localization/city/update.html', context)
    context = {
        'city': cities,
        'governorates': governorate,
        'city_form': city_form,
        'current_page': _('Update'),
        'prev_Page': _('Governorates'),
        'prev_Page_link': reverse_lazy('core:AdminCityList', kwargs={'slug': slug})

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/city/update.html', context)


@authenticated_staff
@staff_only
def AdminCityDelete(request, slug, c_slug):
    governorate = Governorates.objects.get(slug=slug)
    if request.method == "POST":
        try:
            city_object = City.objects.get(slug=c_slug)
            city_object.delete()
            messages.success(request, "City Deleted Successfully", extra_tags='City')
            return HttpResponseRedirect(reverse('core:AdminCityList', kwargs={"slug": governorate.slug}))
        except Exception as e:
            print(e)
            messages.error(request, "City Not Deleted", extra_tags='City')
            return HttpResponseRedirect(reverse('core:AdminCityList', kwargs={"slug": governorate.slug}))


##################Area##############
@authenticated_staff
@staff_only
def AdminAreaList(request, slug):
    city = City.objects.get(slug=slug)
    areas = Area.objects.filter(city=city)
    if request.method == "POST":

        area_form = AdminAreaForm(request.POST or None)
        translate_form = AdminCommonTranslateForm(request.POST or None)
        if area_form:
            name = request.POST.get('name')
            status = request.POST.get('status')
            area_object = Area(city=city, name=name, status=status)
            area_object.save()

            messages.success(request, _("City Add Successfully"), extra_tags='Area')

            return HttpResponseRedirect(reverse('core:AdminAreaList', kwargs={"slug": slug}))
        else:

            messages.error(request, _("Area Not Add"), extra_tags='Area')

    else:
        context = {
            'city': city,
            'areas': areas,
            'area_form': AdminAreaForm(),
            'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Area'),
            'prev_Page': _('City'),
            'prev_Page_link': reverse_lazy('core:AdminCityList', kwargs={'slug': slug})

        }
        return render(request, f'{BACKEND_TEMPLATES}/localization/area/admin.html', context)
    context = {
        'city': city,
        'areas': areas,
        'area_form': AdminAreaForm(),
        'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Area'),
        'prev_Page': _('City'),
        'prev_Page_link': reverse_lazy('core:AdminCityList', kwargs={'slug': slug})

    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/area/admin.html', context)


@authenticated_staff
@staff_only
def AdminAreaUpdate(request, slug, a_slug):
    city = City.objects.get(slug=slug)
    area = Area.objects.get(slug=a_slug)
    if request.method == "POST":
        area_form = AdminAreaForm(request.POST or None, request.FILES or None)
        if area_form:

            name = request.POST.get('name')
            status = request.POST.get('status')

            area_object = Area.objects.get(slug=a_slug)
            area_object.city = city
            area_object.name = name
            area_object.status = status
            area_object.save()
            messages.success(request, "Area Updated Successfully", extra_tags='Area')
            return HttpResponseRedirect(reverse('core:AdminAreaList', kwargs={"slug": slug}))
        else:
            messages.error(request, "Area Not Updated , Please Try Again", extra_tags='Area')

    else:

        context = {
            'city': city,
            'area': area,
            'area_form': AdminAreaForm(),
            'current_page': _('Update'),
            'prev_Page': _('Area'),
            'prev_Page_link': reverse_lazy('core:AdminAreaList', kwargs={'slug': slug})
        }
        return render(request, f'{BACKEND_TEMPLATES}/localization/area/update.html', context)
    context = {
        'city': city,
        'area': area,
        'area_form': AdminAreaForm(),
        'current_page': _('Update'),
        'prev_Page': _('Area'),
        'prev_Page_link': reverse_lazy('core:AdminAreaList', kwargs={'slug': slug})
    }
    return render(request, f'{BACKEND_TEMPLATES}/localization/area/update.html', context)


@authenticated_staff
@staff_only
def AdminAreaDelete(request, slug, a_slug):
    city = City.objects.get(slug=slug)
    if request.method == "POST":
        try:
            area_object = Area.objects.filter(slug=a_slug)
            area_object.delete()
            messages.success(request, "Area Deleted Successfully", extra_tags='Area')
            return HttpResponseRedirect(reverse('core:AdminAreaList', kwargs={"slug": city.slug}))
        except Exception as e:
            print(e)
            messages.error(request, "Area Not Deleted", extra_tags='Area')
            return HttpResponseRedirect(reverse('core:AdminAreaList', kwargs={"slug": city.slug}))
