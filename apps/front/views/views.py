from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from apps.front.forms.forms import *
from apps.front.models.models import *
from core.models.core import *
from core.views.core import *
from helper.commonHelper import *
from helper.decorators import *

User = get_user_model()




####################### Admin Site Setting  #############
@authenticated_staff
@staff_only
def AdminFrontSiteSettingList(request):
    sites = SiteSetting.objects.filter(type='Frontend')


    context = {
        'sites': sites,
        'current_page': _('Site Setting'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/site/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontSiteSettingDetails(request, slug):
    site = SiteSetting.objects.get(slug=slug)
    seo = CommonSeo.objects.filter(Q(owner_id=site.id))
    social = CommonSocialLink.objects.filter(Q(owner_id=site.id))
    context = {
        'site': site,
        'seo': seo,
        'social': social,
        'current_page': _('Site Setting'),
        'prev_Page': _('Site Setting'),
        'prev_Page_link': reverse_lazy('front:AdminSiteSettingList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/site/details.html', context)


@authenticated_staff
@staff_only
def AdminFrontSiteSettingCreate(request):
    if request.method == "POST":
        setting_form = AdminSiteSettingForm(request.POST or None, request.FILES or None)
        social_form = AdminCommonSocialLinkForm(request.POST or None, request.FILES or None)
        seo_form = AdminCommonSeoForm(request.POST or None, request.FILES or None)
        current_domain = get_current_site(request).domain


        if setting_form.is_valid() :

            title = request.POST.get('title')
            keywords = request.POST.get('keywords')
            email = request.POST.get('email')
            copyright = request.POST.get('copyright')
            logo = request.FILES.get('logo')
            dark_logo = request.FILES.get('dark_logo')
            favicon = request.FILES.get('favicon')
            domain = request.POST.get('domain')
            country = request.POST.get('country')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            map = request.POST.get('map')
            about = request.POST.get('about')
            status = request.POST.get('status')
            ######### Socail Link ####
            providers = request.POST.getlist('providers')
            urls = request.POST.getlist('url')

            if domain == '' or domain == None:
                domain = current_domain
            else:
                domain = domain




            setting_object = SiteSetting(title=title, keywords=keywords, copyright=copyright,email=email, logo=logo, dark_logo=dark_logo,
                                        favicon=favicon, domain=domain, country=country,
                                        phone=phone, address=address, map=map, about=about, status=status,
                                        type='Frontend')
            setting_object.save()

            AdminCommonSeo(request, title, keywords, title, request.user.id, setting_object.image,
                           'SiteSetting', setting_object.id)
            site = Site.objects.get(id=1)
            site.title = title
            site.domain = domain
            site.save()
            setting_form.save()
            for url ,provider in zip(urls,providers):

                    AdminCommonSocialLink(request, providers, url, 'SiteSetting', setting_object.id)

            # use django messages framework
            messages.success(request, "Setting Add Successfully, check it out on the home page!", extra_tags='Setting')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontSiteSettingList'))
        else:

            messages.error(request, "Setting Not Add , check it out on the  page!", extra_tags='Setting')

    context = {
        'setting_form': AdminSiteSettingForm(),
        'social_form': AdminCommonSocialLinkForm(),
        'seo_form': AdminCommonSeoForm(),
        'current_page': _('Add'),
        'prev_Page': _('Site Info'),
        'prev_Page_link': reverse_lazy('front:AdminFrontSiteSettingList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/site/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontSiteSettingUpdate(request, slug):
    site = SiteSetting.objects.get(slug=slug)
    social = CommonSocialLink.objects.filter(owner_model=ContentType.objects.get(model='SiteSetting'), owner_id=site.id)
    try:

        seo = CommonSeo.objects.get(owner_model=ContentType.objects.get(model='SiteSetting'),owner_id=site.id)
    except:

        seo = None
    current_domain = get_current_site(request)
    setting_form = AdminSiteSettingUpdateForm()
    social_form = AdminCommonSocialLinkForm()
    seo_form = AdminUpdateCommonSeoForm()

    if request.method == "POST":
        setting_form = AdminSiteSettingUpdateForm(request.POST or None, request.FILES or None)
        social_form = AdminCommonSocialLinkForm(request.POST or None, request.FILES or None)
        seo_form = AdminUpdateCommonSeoForm(request.POST or None, request.FILES or None)
        if setting_form:

            title = request.POST.get('title')
            keywords = request.POST.get('keywords')
            email = request.POST.get('email')
            copyright = request.POST.get('copyright')

            logo = request.FILES.get('logo')
            dark_logo = request.FILES.get('dark_logo')
            favicon = request.FILES.get('favicon')
            domain = request.POST.get('domain')
            country = request.POST.get('country')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            map = request.POST.get('map')
            about = request.POST.get('about')
            status = request.POST.get('status')
            ######### Socail Link ####
            providers = request.POST.getlist('providers')
            url = request.POST.getlist('url')




            setting_object = SiteSetting.objects.get(slug=slug)
            setting_object.title = title
            setting_object.keywords = keywords
            setting_object.copyright = copyright
            setting_object.email = email
            setting_object.domain = domain
            if logo :
                setting_object.logo = logo
            if dark_logo :
                setting_object.dark_logo = dark_logo
            if favicon :
                setting_object.favicon = favicon
            setting_object.country = country
            setting_object.phone = phone
            setting_object.address = address
            setting_object.map = map
            setting_object.about = about
            setting_object.status = status
            setting_object.save()


            j = 0
            for provider in providers:

                if provider != '':
                    try:
                        social = CommonSocialLink.objects.get(Q(owner_id=setting_object.id), Q(provider=provider))
                        social.url = url[j]
                        social.save()
                    except Exception as e:

                        AdminCommonSocialLink(request, provider, url[j], 'SiteSetting', setting_object.id)

                j = j + 1

            AdminCommonSeo(request, title, keywords, title, request.user.id, setting_object.logo,
                           'SiteSetting', setting_object.id)

            messages.success(request,
                             _("Setting Add Successfully, check it out on the home page!"), extra_tags='Setting')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontSiteSettingList'))
        else:

            messages.error(request, _("Setting Not Add , check it out on the  page!"), extra_tags='Setting')

    context = {
        'site': site,
        'social': social,
        'seo': seo,
        'current_domain': current_domain,
        'setting_form': AdminSiteSettingUpdateForm(instance=site),
        'social_form': social_form,
        'seo_form': seo_form,
        'current_page': _('Update'),
        'prev_Page': _('Site Info'),
        'prev_Page_link': reverse_lazy('front:AdminFrontSiteSettingList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/site/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontSiteSettingDelete(request, slug):
    if request.method == "POST":
        try:
            site = SiteSetting.objects.get(slug=slug)
            site.delete()
            messages.success(request, _("Setting Delete Successfully"), extra_tags='Setting')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontSiteSettingList'))
        except Exception as e:
            messages.error(request, _(f"Setting Not Delete , Please Try Again Reason {e}"), extra_tags='Setting')

    else:
        messages.error(request, _("Setting Not Delete , Please Try Again"), extra_tags='Setting')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontSiteSettingList'))









##########################      Front Template   ################################

@authenticated_staff
@staff_only
def AdminFrontTemplateList(request):
    templates = Template.objects.all()

    context = {'templates': templates, 'template_form': AdminTemplateForm(), 'current_page': _('Templates'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/template/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontTemplateCreate(request):
    if request.method == "POST":
        template_form = AdminTemplateForm(request.POST or None, request.FILES or None)
        if template_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')
            image = request.FILES.get('image')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')
            template_form = Template(title=title, keyword=keyword, body=body, status=status, image=image)
            template_form.save()
            translate = CommonTranslate(title=title_tr, keyword=keyword_tr, body=body_tr,
                                        owner_model=ContentType.objects.get(model='Template'),
                                        owner_id=template_form.id)
            translate.save()

            messages.success(request, _("Template Add Successfully"), extra_tags='Template')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontTemplateList'))
        else:

            messages.error(request, _("Template Not Add , Please Try Again"), extra_tags='Template')
    else:
        context = {'template_form': AdminTemplateForm(), 'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Add'), 'prev_Page': _('Templates'),
            'prev_Page_link': reverse_lazy('front:AdminFrontTemplateList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/template/add.html', context)

    context = {'template_form': AdminTemplateForm(), 'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Add'), 'prev_Page': _('Templates'),
        'prev_Page_link': reverse_lazy('front:AdminFrontTemplateList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/template/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontTemplateDetail(request, slug):
    template = Template.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Template'), owner_id=template.id)

    context = {'template': template, 'translate': translate, 'current_page': _('Template'), 'prev_Page': _('Template'),
        'prev_Page_link': reverse_lazy('front:AdminFrontTemplateList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/template/detail.html', context)


@authenticated_staff
@staff_only
def AdminFrontTemplateUpdate(request, slug):
    template = Template.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Template'), owner_id=template.id)

    if request.method == "POST":
        template_form = AdminTemplateForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if template_form.is_valid() and translate_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')
            image = request.FILES.get('image')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')
            template_object = Template.objects.get(id=template.id)
            template_object.title = title
            template_object.keyword = keyword
            template_object.body = body
            template_object.status = status
            template_object.image = image
            template_object.save()
            translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Template'),
                                                    owner_id=template_object.id)
            translate.title = title_tr
            translate.keyword = keyword_tr
            translate.body = body_tr
            translate.save()
            messages.success(request, _("Template Add Successfully"), extra_tags='Template')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontTemplateList'))
        else:

            messages.error(request, _("Template Not Add , Please Try Again"), extra_tags='Template')
    else:
        context = {'template': template, 'translate': translate, 'template_form': AdminTemplateForm(),
            'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Template'),
            'prev_Page_link': reverse_lazy('front:AdminFrontTemplateList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/template/update.html', context)

    context = {'template': template, 'translate': translate, 'template_form': AdminTemplateForm(),
        'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Template'),
        'prev_Page_link': reverse_lazy('front:AdminFrontTemplateList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/template/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontTemplateDelete(request, slug):
    template = Template.objects.get(slug=slug)
    if request.method == "POST":
        template.delete()
        messages.success(request, _("Template Delete Successfully"), extra_tags='Template')
        return HttpResponseRedirect(reverse_lazy('front:AdminFrontTemplateList'))


##########################      Front Category   ################################

@authenticated_staff
@staff_only
def AdminFrontCategoryList(request):
    categories = FrontCategories.objects.all()
    if request.method == "POST":
        category_form = AdminCategoryForm(request.POST or None, request.FILES or None)
        if category_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            category_objet = FrontCategories(title=title, keyword=keyword, status='Active', )
            category_objet.save()
            messages.success(request, _("Category Add Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontCategoryList'))
        else:

            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Category')

    context = {'categories': categories, 'category_form': AdminCategoryForm(), 'current_page': _('Categories'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/category/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontCategoryDetail(request, slug):
    category = FrontCategories.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Categories'),
                                            owner_id=category.id)

    context = {'category': category, 'translate': translate, 'current_page': _('Category'),
        'prev_Page': _('Categories'), 'prev_Page_link': reverse_lazy('front:AdminFrontCategoryList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/category/detail.html', context)


@authenticated_staff
@staff_only
def AdminFrontCategoryUpdate(request, slug):
    category = FrontCategories.objects.get(slug=slug)


    if request.method == "POST":
        category_form = AdminCategoryForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if category_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            status = request.POST.get('status')

            category_object = FrontCategories.objects.get(id=category.id)
            category_object.title = title
            category_object.keyword = keyword
            category_object.status = status
            category_object.save()


            messages.success(request, _("Category Add Successfully"), extra_tags='Category')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontCategoryList'))
        else:

            messages.error(request, _("Category Not Add , Please Try Again"), extra_tags='Category')


    context = {'category': category,  'category_form': AdminCategoryForm(),
        'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Categories'),
        'prev_Page_link': reverse_lazy('front:AdminFrontCategoryList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/category/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontCategoryDelete(request, slug):
    category = FrontCategories.objects.get(slug=slug)
    if request.method == "POST":
        category.delete()
        messages.success(request, _("Category Delete Successfully"), extra_tags='Category')
        return HttpResponseRedirect(reverse_lazy('front:AdminFrontCategoryList'))


##########################      Front Tags   ################################

@authenticated_staff
@staff_only
def AdminFrontTagsList(request):
    tags = Tags.objects.all()
    if request.method == "POST":
        tags_form = AdminTagsForm(request.POST or None, request.FILES or None)
        if tags_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            status = request.POST.get('status')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')
            tags_object = Tags(title=title, keyword=keyword, status=status, )
            tags_object.save()
            translate = CommonTranslate(title=title_tr, keyword=keyword_tr, body=body_tr,
                                        owner_model=ContentType.objects.get(model='Tags'), owner_id=tags_form.id)
            translate.save()

            messages.success(request, _("Tags Add Successfully"), extra_tags='Tags')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontTagsList'))
        else:

            messages.error(request, _("Tags Not Add , Please Try Again"), extra_tags='Tags')
    else:
        context = {'tags': tags, 'tags_form': AdminTagsForm(), 'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Add'), 'prev_Page': _('Tags'),
            'prev_Page_link': reverse_lazy('front:AdminFrontTagsList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/tags/admin.html', context)

    context = {'tags': tags, 'tags_form': AdminTagsForm(), 'current_page': _('Tags'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/tags/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontTagsDetail(request, slug):
    tags = Tags.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Tags'), owner_id=tags.id)

    context = {'tags': tags, 'translate': translate, 'current_page': _('Tags'), 'prev_Page': _('Tags'),
        'prev_Page_link': reverse_lazy('front:AdminFrontTagsList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/tags/detail.html', context)


@authenticated_staff
@staff_only
def AdminFrontTagsUpdate(request, slug):
    tags = Tags.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Tags'), owner_id=tags.id)

    if request.method == "POST":
        tags_form = AdminTagsForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if tags_form.is_valid() and translate_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')
            image = request.FILES.get('image')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')
            tags_object = Tags.objects.get(id=tags.id)
            tags_object.title = title
            tags_object.keyword = keyword
            tags_object.body = body
            tags_object.status = status
            tags_object.image = image
            tags_object.save()
            translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Tags'),
                                                    owner_id=tags_object.id)
            translate.title = title_tr
            translate.keyword = keyword_tr
            translate.body = body_tr
            translate.save()
            messages.success(request, _("Tags Add Successfully"), extra_tags='Tags')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontTagsList'))
        else:

            messages.error(request, _("Tags Not Add , Please Try Again"), extra_tags='Tags')
    else:
        context = {'tags': tags, 'translate': translate, 'tags_form': AdminTagsForm(),
            'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Tags'),
            'prev_Page_link': reverse_lazy('front:AdminFrontTagsList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/tags/update.html', context)

    context = {'tags': tags, 'translate': translate, 'tags_form': AdminTagsForm(),
        'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Tags'),
        'prev_Page_link': reverse_lazy('front:AdminFrontTagsList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/tags/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontTagsDelete(request, slug):
    tags = Tags.objects.get(slug=slug)
    if request.method == "POST":
        tags.delete()
        messages.success(request, _("Tags Delete Successfully"), extra_tags='Tags')
        return HttpResponseRedirect(reverse_lazy('front:AdminFrontTagsList'))


##########################      Front Pages   ################################

@authenticated_staff
@staff_only
def AdminFrontPagesList(request):
    pages = Pages.objects.all()
    if request.method == "POST":
        pages_form = AdminPagesForm(request.POST or None, request.FILES or None)
        if pages_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')

            status = request.POST.get('status')
            image = request.FILES.get('image')

            pages_form = Pages(title=title, keyword=keyword, status=status, image=image)
            pages_form.save()

            messages.success(request, _("Pages Add Successfully"), extra_tags='Pages')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontPagesList'))
        else:

            messages.error(request, _("Pages Not Add , Please Try Again"), extra_tags='Pages')

    context = {'pages': pages, 'pages_form': AdminPagesForm(), 'current_page': _('Pages'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/pages/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontPagesCreate(request):
    if request.method == "POST":
        pages_form = AdminPagesForm(request.POST or None, request.FILES or None)
        if pages_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')
            image = request.FILES.get('image')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')
            pages_form = Pages(title=title, keyword=keyword, body=body, status=status, image=image)
            pages_form.save()
            translate = CommonTranslate(title=title_tr, keyword=keyword_tr, body=body_tr,
                                        owner_model=ContentType.objects.get(model='Pages'), owner_id=pages_form.id)
            translate.save()

            messages.success(request, _("Pages Add Successfully"), extra_tags='Pages')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontPagesList'))
        else:

            messages.error(request, _("Pages Not Add , Please Try Again"), extra_tags='Pages')
    else:
        context = {'pages_form': AdminPagesForm(), 'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Add'), 'prev_Page': _('Pages'),
            'prev_Page_link': reverse_lazy('front:AdminFrontPagesList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/pages/add.html', context)

    context = {'pages_form': AdminPagesForm(), 'translate_form': AdminCommonTranslateForm(), 'current_page': _('Add'),
        'prev_Page': _('Pages'), 'prev_Page_link': reverse_lazy('front:AdminFrontPagesList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/pages/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontPagesDetail(request, slug):
    pages = Pages.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Pages'), owner_id=pages.id)

    context = {'pages': pages, 'translate': translate, 'current_page': _('Pages'), 'prev_Page': _('Pages'),
        'prev_Page_link': reverse_lazy('front:AdminFrontPagesList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/pages/detail.html', context)


@authenticated_staff
@staff_only
def AdminFrontPagesUpdate(request, slug):
    pages = Pages.objects.get(slug=slug)


    if request.method == "POST":
        pages_form = AdminPagesForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if pages_form.is_valid() and translate_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')
            image = request.FILES.get('image')

            pages_object = Pages.objects.get(id=pages.id)
            pages_object.title = title
            pages_object.keyword = keyword
            pages_object.body = body
            pages_object.status = status
            pages_object.image = image
            pages_object.save()

            messages.success(request, _("Pages Add Successfully"), extra_tags='Pages')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontPagesList'))
        else:

            messages.error(request, _("Pages Not Add , Please Try Again"), extra_tags='Pages')


    context = {'pages': pages,  'pages_form': AdminPagesForm(),
        'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Pages'),
        'prev_Page_link': reverse_lazy('front:AdminFrontPagesList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/pages/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontPagesDelete(request, slug):
    pages = Pages.objects.get(slug=slug)
    if request.method == "POST":
        pages.delete()
        messages.success(request, _("Pages Delete Successfully"), extra_tags='Pages')
        return HttpResponseRedirect(reverse_lazy('front:AdminFrontPagesList'))


##########################      Front Sections   ################################


@authenticated_staff
@staff_only
def AdminFrontSectionsList(request):
    sections = Sections.objects.all()
    sections_form = AdminSectionsForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if sections_form:
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            position = request.POST.get('position')
            page = request.POST.get('page')
            visibility = request.POST.get('visibility')

            if page == 'None' or page == '':
                page = None
            else:
                page = Pages.objects.get(id=page)
            sections_object = Sections(title=title, keyword=keyword, position=position, page=page,
                                       visibility=visibility)
            sections_object.save()
            messages.success(request, _("Sections Add Successfully"), extra_tags='Sections')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontSectionsList'))
        else:

            messages.error(request, _("Sections Not Add , Please Try Again"), extra_tags='Sections')

    context = {'sections': sections, 'sections_form': AdminSectionsForm(), 'current_page': _('Sections'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/sections/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontSectionsCreate(request):
    if request.method == "POST":
        sections_form = AdminSectionsForm(request.POST or None, request.FILES or None)
        if sections_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')
            image = request.FILES.get('image')
            template = request.POST.get('template')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')
            sections_form = Sections(title=title, keyword=keyword, body=body, status=status, image=image,
                                     template=Template.objects.get(id=template))
            sections_form.save()
            translate = CommonTranslate(title=title_tr, keyword=keyword_tr, body=body_tr,
                                        owner_model=ContentType.objects.get(model='Sections'),
                                        owner_id=sections_form.id)
            translate.save()

            messages.success(request, _("Sections Add Successfully"), extra_tags='Sections')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontSectionsList'))
        else:

            messages.error(request, _("Sections Not Add , Please Try Again"), extra_tags='Sections')
    else:
        context = {'sections_form': AdminSectionsForm(), 'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Add'), 'prev_Page': _('Sections'),
            'prev_Page_link': reverse_lazy('front:AdminFrontSectionsList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/sections/add.html', context)

    context = {'sections_form': AdminSectionsForm(), 'translate_form': AdminCommonTranslateForm(),
        'current_page': _('Add'), 'prev_Page': _('Sections'),
        'prev_Page_link': reverse_lazy('front:AdminFrontSectionsList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/sections/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontSectionsDetail(request, slug):
    sections = Sections.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Sections'), owner_id=sections.id)

    context = {'sections': sections, 'translate': translate, 'current_page': _('Sections'), 'prev_Page': _('Sections'),
        'prev_Page_link': reverse_lazy('front:AdminFrontSectionsList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/sections/detail.html', context)


@authenticated_staff
@staff_only
def AdminFrontSectionsUpdate(request, slug):
    sections = Sections.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Sections'), owner_id=sections.id)

    if request.method == "POST":
        sections_form = AdminSectionsForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if sections_form.is_valid() and translate_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')
            image = request.FILES.get('image')
            template = request.POST.get('template')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')
            sections_object = Sections.objects.get(id=sections.id)
            sections_object.title = title
            sections_object.keyword = keyword
            sections_object.body = body
            sections_object.status = status
            sections_object.image = image
            sections_object.template = Template.objects.get(id=template)
            sections_object.save()
            translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Sections'),
                                                    owner_id=sections_object.id)
            translate.title = title_tr
            translate.keyword = keyword_tr
            translate.body = body_tr
            translate.save()
            messages.success(request, _("Sections Add Successfully"), extra_tags='Sections')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontSectionsList'))
        else:

            messages.error(request, _("Sections Not Add , Please Try Again"), extra_tags='Sections')
    else:
        context = {'sections': sections, 'translate': translate, 'sections_form': AdminSectionsForm(),
            'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Sections'),
            'prev_Page_link': reverse_lazy('front:AdminFrontSectionsList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/sections/update.html', context)

    context = {'sections': sections, 'translate': translate, 'sections_form': AdminSectionsForm(),
        'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Sections'),
        'prev_Page_link': reverse_lazy('front:AdminFrontSectionsList'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/sections/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontSectionsDelete(request, slug):
    sections = Sections.objects.get(slug=slug)
    if request.method == "POST":
        sections.delete()
        messages.success(request, _("Sections Delete Successfully"), extra_tags='Sections')
        return HttpResponseRedirect(reverse_lazy('front:AdminFrontSectionsList'))


##########################      Front Menu   ################################


@authenticated_staff
@staff_only
def AdminFrontMenuList(request):
    menu = Menu.objects.all()

    context = {'menu': menu, 'menu_form': AdminMenuForm(), 'current_page': _('Menu'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/menu/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontMenuCreate(request):
    if request.method == "POST":
        menu_form = AdminMenuForm(request.POST or None, request.FILES or None)
        if menu_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')
            menu_form = Menu(title=title, keyword=keyword, body=body, status=status)
            menu_form.save()
            translate = CommonTranslate(title=title_tr, keyword=keyword_tr, body=body_tr,
                                        owner_model=ContentType.objects.get(model='Menu'), owner_id=menu_form.id)
            translate.save()

            messages.success(request, _("Menu Add Successfully"), extra_tags='Menu')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontMenuList'))
        else:

            messages.error(request, _("Menu Not Add , Please Try Again"), extra_tags='Menu')
    else:
        context = {'menu_form': AdminMenuForm(), 'translate_form': AdminCommonTranslateForm(), 'current_page': _('Add'),
            'prev_Page': _('Menu'), 'prev_Page_link': reverse_lazy('front:AdminFrontMenuList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/menu/add.html', context)

    context = {'menu_form': AdminMenuForm(), 'translate_form': AdminCommonTranslateForm(), 'current_page': _('Add'),
        'prev_Page': _('Menu'), 'prev_Page_link': reverse_lazy('front:AdminFrontMenuList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/menu/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontMenuDetail(request, slug):
    menu = Menu.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Menu'), owner_id=menu.id)

    context = {'menu': menu, 'translate': translate, 'current_page': _('Menu'), 'prev_Page': _('Menu'),
        'prev_Page_link': reverse_lazy('front:AdminFrontMenuList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/menu/detail.html', context)


@authenticated_staff
@staff_only
def AdminFrontMenuUpdate(request, slug):
    menu = Menu.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Menu'), owner_id=menu.id)

    if request.method == "POST":
        menu_form = AdminMenuForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if menu_form.is_valid() and translate_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')

            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')

            menu_object = Menu.objects.get(id=menu.id)
            menu_object.title = title
            menu_object.keyword = keyword
            menu_object.body = body
            menu_object.status = status
            menu_object.save()
            translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Menu'),
                                                    owner_id=menu_object.id)
            translate.title = title_tr
            translate.keyword = keyword_tr
            translate.body = body_tr
            translate.save()
            messages.success(request, _("Menu Add Successfully"), extra_tags='Menu')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontMenuList'))
        else:

            messages.error(request, _("Menu Not Add , Please Try Again"), extra_tags='Menu')
    else:
        context = {'menu': menu, 'translate': translate, 'menu_form': AdminMenuForm(),
            'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Menu'),
            'prev_Page_link': reverse_lazy('front:AdminFrontMenuList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/menu/update.html', context)

    context = {'menu': menu, 'translate': translate, 'menu_form': AdminMenuForm(),
        'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Menu'),
        'prev_Page_link': reverse_lazy('front:AdminFrontMenuList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/menu/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontMenuDelete(request, slug):
    menu = Menu.objects.get(slug=slug)
    if request.method == "POST":
        menu.delete()
        messages.success(request, _("Menu Delete Successfully"), extra_tags='Menu')
        return HttpResponseRedirect(reverse_lazy('front:AdminFrontMenuList'))


##########################      Front Slider   ################################

@authenticated_staff
@staff_only
def AdminFrontSliderList(request):
    sliders = Slider.objects.all()
    slider_items = SliderItem.objects.all()

    context = {'sliders': sliders, 'slider_items': slider_items, 'slider_form': AdminSliderForm(),
        'current_page': _('Slider'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/slider/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontSliderCreate(request):
    if request.method == "POST":
        slider_form = AdminSliderForm(request.POST or None, request.FILES or None)
        if slider_form:

            title = request.POST.getlist('[title]')
            category = request.POST.getlist('[category]')
            keywords = request.POST.getlist('[keywords]')
            url = request.POST.getlist('[url]')
            image = request.FILES.get('[image]')

            try:
                slider_object = Slider.objects.get(title='HomeSlider', type='HomeSlider')
            except:

                slider_object = Slider(title='HomeSlider', type='HomeSlider')
                slider_object.save()

            slider_object.save()
            i = 0
            for i in title:
                slider_item_object = SliderItem(slider=slider_object, title=title[i], category=category[i], url=url[i],
                                                image=image[i], keywords=keywords[i], type='HomeSlider')
                slider_item_object.save()
                i +=1

        messages.success(request, _("Slider Add Successfully"), extra_tags='Slider')

        return HttpResponseRedirect(reverse_lazy('front:AdminFrontSliderList'))
    else:

        messages.error(request, _("Slider Not Add , Please Try Again"), extra_tags='Slider')

    context = {'slider_form': AdminSliderForm(),

        'current_page': _('Add'), 'prev_Page': _('Slider'),
        'prev_Page_link': reverse_lazy('front:AdminFrontSliderList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/slider/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontSliderDetail(request, slug):
    slider = Slider.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Slider'), owner_id=slider.id)

    context = {'slider': slider, 'translate': translate, 'current_page': _('Slider'), 'prev_Page': _('Slider'),
        'prev_Page_link': reverse_lazy('front:AdminFrontSliderList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/slider/detail.html', context)


@authenticated_staff
@staff_only
def AdminFrontSliderUpdate(request, slug):
    slider = Slider.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Slider'), owner_id=slider.id)

    if request.method == "POST":
        slider_form = AdminSliderForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if slider_form.is_valid() and translate_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')

            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')

            slider_object = Slider.objects.get(id=slider.id)
            slider_object.title = title
            slider_object.keyword = keyword
            slider_object.body = body
            slider_object.status = status
            slider_object.save()
            translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Slider'),
                                                    owner_id=slider_object.id)
            translate.title = title_tr
            translate.keyword = keyword_tr
            translate.body = body_tr
            translate.save()
            messages.success(request, _("Slider Add Successfully"), extra_tags='Slider')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontSliderList'))
        else:

            messages.error(request, _("Slider Not Add , Please Try Again"), extra_tags='Slider')
    else:
        context = {'slider': slider, 'translate': translate, 'slider_form': AdminSliderForm(),
            'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Slider'),
            'prev_Page_link': reverse_lazy('front:AdminFrontSliderList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/slider/update.html', context)

    context = {'slider': slider, 'translate': translate, 'slider_form': AdminSliderForm(),
        'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Slider'),
        'prev_Page_link': reverse_lazy('front:AdminFrontSliderList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/slider/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontSliderDelete(request, slug):
    slider = SliderItem.objects.get(slug=slug)
    if request.method == "POST":
        slider.delete()
        messages.success(request, _("Slider Delete Successfully"), extra_tags='Slider')
        return HttpResponseRedirect(reverse_lazy('front:AdminFrontSliderList'))


##########################      Front Banner   ################################

@authenticated_staff
@staff_only
def AdminFrontBannerList(request):
    banners = Banner.objects.all()

    context = {'banners': banners, 'banner_form': AdminBannerForm(), 'current_page': _('Banner'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/banner/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontBannerCreate(request):
    if request.method == "POST":
        banner_form = AdminBannerForm(request.POST or None, request.FILES or None)
        if banner_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')


            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')

            banner_form = Banner(title=title, keyword=keyword, body=body, )
            banner_form.save()
            translate = CommonTranslate(title=title_tr, keyword=keyword_tr, body=body_tr,
                                        owner_model=ContentType.objects.get(model='Banner'), owner_id=banner_form.id)
            translate.save()

            messages.success(request, _("Banner Add Successfully"), extra_tags='Banner')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontBannerList'))
        else:

            messages.error(request, _("Banner Not Add , Please Try Again"), extra_tags='Banner')
    else:
        context = {'banner_form': AdminBannerForm(), 'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Add'), 'prev_Page': _('Banner'),
            'prev_Page_link': reverse_lazy('front:AdminFrontBannerList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/banner/add.html', context)

    context = {'banner_form': AdminBannerForm(), 'translate_form': AdminCommonTranslateForm(), 'current_page': _('Add'),
        'prev_Page': _('Banner'), 'prev_Page_link': reverse_lazy('front:AdminFrontBannerList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/banner/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontBannerDetail(request, slug):
    banner = Banner.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Banner'), owner_id=banner.id)

    context = {'banner': banner, 'translate': translate, 'current_page': _('Banner'), 'prev_Page': _('Banner'),
        'prev_Page_link': reverse_lazy('front:AdminFrontBannerList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/banner/detail.html', context)


@authenticated_staff
@staff_only
def AdminFrontBannerUpdate(request, slug):
    banner = Banner.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Banner'), owner_id=banner.id)

    if request.method == "POST":
        banner_form = AdminBannerForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if banner_form.is_valid() and translate_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')

            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')

            banner_object = Banner.objects.get(id=banner.id)
            banner_object.title = title
            banner_object.keyword = keyword
            banner_object.body = body
            banner_object.status = status
            banner_object.save()
            translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Banner'),
                                                    owner_id=banner_object.id)
            translate.title = title_tr
            translate.keyword = keyword_tr
            translate.body = body_tr
            translate.save()
            messages.success(request, _("Banner Add Successfully"), extra_tags='Banner')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontBannerList'))
        else:

            messages.error(request, _("Banner Not Add , Please Try Again"), extra_tags='Banner')
    else:
        context = {'banner': banner, 'translate': translate, 'banner_form': AdminBannerForm(),
            'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Banner'),
            'prev_Page_link': reverse_lazy('front:AdminFrontBannerList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/banner/update.html', context)

    context = {'banner': banner, 'translate': translate, 'banner_form': AdminBannerForm(),
        'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Banner'),
        'prev_Page_link': reverse_lazy('front:AdminFrontBannerList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/banner/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontBannerDelete(request, slug):
    banner = Banner.objects.get(slug=slug)
    if request.method == "POST":
        banner.delete()
        messages.success(request, _("Banner Delete Successfully"), extra_tags='Banner')
        return HttpResponseRedirect(reverse_lazy('front:AdminFrontBannerList'))


##########################      Front Block   ################################

@authenticated_staff
@staff_only
def AdminFrontBlockList(request):
    blocks = Block.objects.all()
    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)
        if block_form:
            title = request.POST.get('title')
            # category = request.POST.get('category')
            # page = request.POST.get('page')
            # section = request.POST.get('section')
            section = request.POST.get('section')
            keywords = request.POST.get('keywords')
            keywords2 = request.POST.get('keywords2')
            image = request.FILES.get('image')
            image_url = request.POST.get('image_url')
            url = request.POST.get('url')
            details_page = request.POST.get('details_page')
            type = request.POST.get('type')
            order = request.POST.get('order')

            try:
                block_object = Block.objects.get(type=type)
                block_object.title =title
                block_object.keywords = keywords
                block_object.keywords2 = keywords2
                block_object.save()
            except Exception as e:
                print(e)
                block_object = Block(title=title,  section=section, keywords=keywords,keywords2=keywords2,
                                     image=image, image_url=image_url, url=url, details_page=details_page, type=type,
                                     order=order)
                block_object.save()

            messages.success(request, _("Block Add Successfully"), extra_tags='Block')

            return redirect(request.META['HTTP_REFERER'])
        else:

            messages.error(request, _("Block Not Add , Please Try Again"), extra_tags='Block')

    context = {'blocks': blocks, 'block_form': AdminBlockForm(), 'current_page': _('Block'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/block/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontBlockCreate(request):
    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)
        if block_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')

            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')

            block_form = Block(title=title, keyword=keyword, body=body, status=status)
            block_form.save()
            translate = CommonTranslate(title=title_tr, keyword=keyword_tr, body=body_tr,
                                        owner_model=ContentType.objects.get(model='Block'), owner_id=block_form.id)
            translate.save()

            messages.success(request, _("Block Add Successfully"), extra_tags='Block')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontBlockList'))
        else:

            messages.error(request, _("Block Not Add , Please Try Again"), extra_tags='Block')
    else:
        context = {'block_form': AdminBlockForm(), 'translate_form': AdminCommonTranslateForm(),
            'current_page': _('Add'), 'prev_Page': _('Block'),
            'prev_Page_link': reverse_lazy('front:AdminFrontBlockList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/block/add.html', context)

    context = {'block_form': AdminBlockForm(), 'translate_form': AdminCommonTranslateForm(), 'current_page': _('Add'),
        'prev_Page': _('Block'), 'prev_Page_link': reverse_lazy('front:AdminFrontBlockList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/block/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontBlockDetail(request, slug):
    block = Block.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Block'), owner_id=block.id)

    context = {'block': block, 'translate': translate, 'current_page': _('Block'), 'prev_Page': _('Block'),
        'prev_Page_link': reverse_lazy('front:AdminFrontBlockList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/block/detail.html', context)


@authenticated_staff
@staff_only
def AdminFrontBlockUpdate(request, slug):
    block = Block.objects.get(slug=slug)
    translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Block'), owner_id=block.id)

    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)
        translate_form = AdminCommonTranslateForm(request.POST or None, request.FILES or None)
        if block_form.is_valid() and translate_form.is_valid():
            title = request.POST.get('title')
            keyword = request.POST.get('keyword')
            body = request.POST.get('body')
            status = request.POST.get('status')
            title_tr = request.POST.get('title_tr')
            keyword_tr = request.POST.get('keyword_tr')
            body_tr = request.POST.get('body_tr')

            block_object = Block.objects.get(id=block.id)
            block_object.title = title
            block_object.keyword = keyword
            block_object.body = body
            block_object.status = status
            block_object.save()
            translate = CommonTranslate.objects.get(owner_model=ContentType.objects.get(model='Block'),
                                                    owner_id=block_object.id)
            translate.title = title_tr
            translate.keyword = keyword_tr
            translate.body = body_tr
            translate.save()
            messages.success(request, _("Block Add Successfully"), extra_tags='Block')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontBlockList'))
        else:

            messages.error(request, _("Block Not Add , Please Try Again"), extra_tags='Block')
    else:
        context = {'block': block, 'translate': translate, 'block_form': AdminBlockForm(),
            'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Block'),
            'prev_Page_link': reverse_lazy('front:AdminFrontBlockList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/block/update.html', context)

    context = {'block': block, 'translate': translate, 'block_form': AdminBlockForm(),
        'translate_form': AdminCommonTranslateForm(), 'current_page': _('Update'), 'prev_Page': _('Block'),
        'prev_Page_link': reverse_lazy('front:AdminFrontBlockList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/block/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontBlockDelete(request, slug):
    block = Block.objects.get(slug=slug)
    if request.method == "POST":
        block.delete()
        messages.success(request, _("Block Delete Successfully"), extra_tags='Block')
        return HttpResponseRedirect(reverse_lazy('front:AdminFrontBlockList'))

@authenticated_staff
@staff_only
def AdminFrontBlockDeleteFromUpdate(request, slug):

    if request.method == "POST":
        try:
            block_item = Block.objects.get(slug=slug)
            block_item.image = None
            block_item.save()
            message = _("Block Item Delete Successfully")
            return JsonResponse({'status': 'ok', 'message': message},
                            safe=False)
        except:
            message = _("Block Item Not Delete")
            return JsonResponse({'status': 'ok', 'message': message},
                            safe=False)


@authenticated_staff
@staff_only
def AdminFrontBlockDeleteItemAllFromUpdate(request, slug):

    if request.method == "POST":
        try:
            block_item = BlockItem.objects.get(slug=slug)
            block_item.delete()
            message = _("Block Item Delete Successfully")
            return JsonResponse({'status': 'ok', 'message': message},
                            safe=False)
        except:
            message = _("Block Item Not Delete")
            return JsonResponse({'status': 'ok', 'message': message},
                            safe=False)


@authenticated_staff
@staff_only
def AdminFrontBlockDeleteItemFromUpdate(request, slug):
    if request.method == "POST":
        try:
            block_item = BlockItem.objects.get(slug=slug)
            block_item.image = None
            block_item.save()

            message = _("Block Item Delete Successfully")
            return JsonResponse({'status': 'ok', 'message': message},
                                safe=False)
        except:
            message = _("Block Item Not Delete")
            return JsonResponse({'status': 'ok', 'message': message},
                                safe=False)

@authenticated_staff
@staff_only
def AdminFrontTestimonialDelete(request, slug):
    testimonial = Testimonial.objects.get(slug=slug)
    if request.method == "POST":
        testimonial.delete()
        messages.success(request, _("Testimonial Delete Successfully"), extra_tags='Testimonial')
        return HttpResponseRedirect(reverse_lazy('front:AdminFrontTestimonialList'))
