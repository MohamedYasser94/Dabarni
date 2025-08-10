from datetime import datetime
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from apps.front.forms.forms import *
from apps.front.models.models import *
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staff, staff_only

User = get_user_model()

##########################      Front Testimonial   ################################

@authenticated_staff
@staff_only
def AdminFrontTestimonialList(request):
    testimonials = TestimonialItem.objects.all()

    testimonial_form = AdminTestimonialForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if testimonial_form:
            title = request.POST.get('title')

            try:
                testimonial_object = Testimonial.objects.get(type='Testimonial',)
                testimonial_object.title = title
                testimonial_object.status = 'Active'
                testimonial_object.save()
            except:
                testimonial_object = Testimonial(title=title, type='Testimonial',
                                                 status='Active')
                testimonial_object.save()
            messages.success(request, _("Testimonial Add Successfully"), extra_tags='Testimonial')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontTestimonialList'))
        else:

            messages.error(request, _("Testimonial Not Add , Please Try Again"), extra_tags='Testimonial')

    context = {'testimonials': testimonials, 'testimonial_form': AdminTestimonialForm(),
        'current_page': _('Testimonial'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/testimonial/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontTestimonialCreate(request):
    if request.method == 'POST':
        testimonial_form = AdminTestimonialItemForm(request.POST, request.FILES)
        if testimonial_form:
            title = request.POST.get('title')
            description = request.POST.get('description')
            keywords = request.POST.get('keywords')
            image = request.FILES.get('image')
            status = request.POST.get('status')
            try:

                testimonial = Testimonial.objects.get(type='Testimonial')
            except:

                messages.error(request, _("Testimonial Not Found please Create Testimonial Title First"), extra_tags='Testimonial')
                return HttpResponseRedirect(reverse_lazy('front:AdminFrontTestimonialList'))

            testimonial_object = TestimonialItem(testimonial=testimonial,title=title, description=description, keywords=keywords, image=image,
                                             status=status)
            testimonial_object.save()
            messages.success(request, _("Testimonial Add Successfully"), extra_tags='Testimonial')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontTestimonialList'))
        else:

            messages.error(request, _("Testimonial Not Add , Please Try Again"), extra_tags='Testimonial')

    else:
        testimonial_form = AdminTestimonialItemForm()

    context = {'testimonial_form': testimonial_form, 'current_page': _('Testimonial'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/testimonial/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontTestimonialUpdate(request, slug):
    testimonial = TestimonialItem.objects.get(slug=slug)

    if request.method == "POST":
        testimonial_form = AdminTestimonialForm(request.POST or None, request.FILES or None)

        if testimonial_form:
            title = request.POST.get('title')
            description = request.POST.get('description')
            description2 = request.POST.get('description2')
            keywords = request.POST.get('keywords')
            image = request.FILES.get('image')
            status = request.POST.get('status')

            testimonial_object = TestimonialItem.objects.get(id=testimonial.id)
            testimonial_object.title = title
            testimonial_object.description = description
            testimonial_object.description2 = description2
            testimonial_object.keywords = keywords
            if image:
                testimonial_object.image = image
            else:
                testimonial_object.image = testimonial.image
            testimonial_object.status = status
            testimonial_object.save()

            messages.success(request, _("Testimonial Add Successfully"), extra_tags='Testimonial')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontTestimonialList'))
        else:

            messages.error(request, _("Testimonial Not Add , Please Try Again"), extra_tags='Testimonial')
    else:
        context = {'testimonial': testimonial,

            'testimonial_form': AdminTestimonialForm(),

            'current_page': _('Update'), 'prev_Page': _('Testimonial'),
            'prev_Page_link': reverse_lazy('front:AdminFrontTestimonialList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/blocks/testimonial/update.html', context)

    context = {'testimonial': testimonial,

        'testimonial_form': AdminTestimonialForm(),

        'current_page': _('Update'), 'prev_Page': _('Testimonial'),
        'prev_Page_link': reverse_lazy('front:AdminFrontTestimonial'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/testimonial/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontTestimonialDelete(request, slug):
    testimonial = TestimonialItem.objects.get(slug=slug)
    testimonial.delete()
    messages.success(request, _("Testimonial Delete Successfully"), extra_tags='Testimonial')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontTestimonialList'))


@authenticated_staff
@staff_only
def AdminFrontTestimonialDeleteItemFromUpdate(request, slug):
    if request.method == "POST":
        try:
            testimonial = TestimonialItem.objects.get(slug=slug)
            testimonial.image = None
            testimonial.save()
            message = 'Testimonial Image Delete Successfully'

            return JsonResponse({'status': 'ok', 'message': message},
                                safe=False)

        except:
            message = 'Testimonial Image Not Delete'
            return JsonResponse({'status': 'error', 'message': message}
                                , safe=False)


################### Front Block Client #############################

@authenticated_staff
@staff_only
def AdminFrontOurClientList(request):
    blocks = Block.objects.filter(type='Client')
    block_items = BlockItem.objects.filter(type='Client')
    if request.method == 'POST':
        block_form = AdminBlockForm(request.POST, request.FILES)
        if block_form:
            title = request.POST.get('title')
            keywords2 = request.POST.get('keywords2')
            keywords = request.POST.get('keywords')
            category = request.POST.get('category')

            page = request.POST.get('page')
            order = request.POST.get('order')
            section = request.POST.get('section')
            description = request.POST.get('description')



            if category == '' or category == None:
                category = None
            else:
                category = FrontCategories.objects.get(id=category)

            if page == '' or page == None:
                page = None
            else:
                page = Pages.objects.get(id=page)



            try:
                block_object = Block.objects.get(type='Client')
                block_object.title = title
                block_object.keywords= keywords
                block_object.keywords2 = keywords2
                block_object.save()
            except:
                block_object = Block(title=title, keywords=keywords,keywords2=keywords2, category=category, page=page, section=section,
                                     description=description, type='Client', order=0)
                block_object.save()


            messages.success(request, _('Our Clients Created Successfully'), extra_tags='OurClients')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontOurClientList'))
        else:
            messages.error(request, _('Our Clients Not Created'), extra_tags='OurClients')

    else:
        block_form = AdminBlockForm()

    context = {'blocks': blocks,'block_items':block_items, 'block_form': AdminBlockForm(), 'current_page': _('Our Clients'),


               }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/client/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontOurClientCreate(request):
    try:
        block_object = Block.objects.get(type='Client')
    except:
        block_object = Block( type='Client', order=0)
        block_object.save()
    if request.method == 'POST':
        block_form = AdminBlockItemForm(request.POST, request.FILES)
        if block_form:
            item_order = request.POST.get('item_order')
            ######### images  block item ##########
            item_title = request.POST.get('item_title')
            item_images = request.FILES.get('item_images')
            item_description = request.POST.get('item_description')

            if item_order == '' or item_order == None:
                item_order = 0
            block_item = BlockItem(block=block_object, type='Client', title=item_title, description=item_description,
                                   image=item_images,
                                   order=item_order)
            block_item.save()
            messages.success(request, _('Our Clients Created Successfully'), extra_tags='OurClients')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontOurClientList'))
        else:
            messages.error(request, _('Our Clients Not Created'), extra_tags='OurClients')
    else:
        block_form = AdminBlockForm()

    context = {'block': block_object, 'block_form': AdminBlockItemForm(), 'current_page': _('Our Clients'),


               }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/client/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontOurClientUpdate(request,slug):
    block_item = BlockItem.objects.get(slug=slug)
    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)

        if block_form:


            ######### images  block item ##########
            title = request.POST.get('title')
            image = request.FILES.get('image')
            order = request.POST.get('order')
            status = request.POST.get('status')

            block_item_object = BlockItem.objects.get(id=block_item.id)
            block_item_object.title = title
            if image:
                block_item_object.image = image

            block_item_object.order = order
            block_item_object.status = status

            block_item_object.save()

            messages.success(request, _("Our Clients Add Successfully"), extra_tags='OurClients')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontOurClientList'))
        else:

            messages.error(request, _("Our Clients Not Add , Please Try Again"), extra_tags='OurClients')
    else:
        context = {'block_item': block_item, 'block_form': AdminBlockForm(),

            'current_page': _('Update'), 'prev_Page': _('Our Clients'),
            'prev_Page_link': reverse_lazy('front:AdminFrontOurClientList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/blocks/client/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontOurClientDelete(request,slug):

    block_item = BlockItem.objects.get(slug=slug)

    block_item.delete()
    messages.success(request, _("Our Client Delete Successfully"), extra_tags='AboutPage')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontOurClientList'))



################### Front Block Team #############################

@authenticated_staff
@staff_only
def AdminFrontOurTeamList(request):
    blocks = Block.objects.filter(type='Team')
    block_items = BlockItem.objects.filter(type='Team')
    if request.method == 'POST':
        block_form = AdminBlockForm(request.POST, request.FILES)
        if block_form:
            title = request.POST.get('title')
            keywords2 = request.POST.get('keywords2')
            keywords = request.POST.get('keywords')
            category = request.POST.get('category')

            page = request.POST.get('page')
            order = request.POST.get('order')
            section = request.POST.get('section')
            description = request.POST.get('description')



            if category == '' or category == None:
                category = None
            else:
                category = FrontCategories.objects.get(id=category)

            if page == '' or page == None:
                page = None
            else:
                page = Pages.objects.get(id=page)



            try:
                block_object = Block.objects.get(type='Team')
                block_object.title = title
                block_object.keywords= keywords
                block_object.keywords2 = keywords2
                block_object.save()
            except:
                block_object = Block(title=title, keywords=keywords,keywords2=keywords2, category=category, page=page, section=section,
                                     description=description, type='Team', order=0)
                block_object.save()


            messages.success(request, _('Our Clients Created Successfully'), extra_tags='OurTeam')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontOurTeamList'))
        else:
            messages.error(request, _('Our Clients Not Created'), extra_tags='OurTeam')

    else:
        block_form = AdminBlockForm()

    context = {'blocks': blocks,'block_items':block_items, 'block_form': AdminBlockForm(), 'current_page': _('Our Team'),


               }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/team/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontOurTeamCreate(request):
    try:
        block_object = Block.objects.get(type='Team')
    except:
        block_object = Block( type='Team', order=0)
        block_object.save()
    if request.method == 'POST':
        block_form = AdminBlockItemForm(request.POST, request.FILES)
        if block_form:

            ######### images  block item ##########
            title = request.POST.get('title')
            keywords = request.POST.get('keywords')
            number = request.POST.get('number')
            email = request.POST.get('email')
            order = request.POST.get('order')
            image = request.FILES.get('image')

            if order == '' or order == None:
                order = 0
            block_item = BlockItem(block=block_object, type='Team', title=title, keywords=keywords, number=number, email=email,
                                   image=image,
                                   order=order)
            block_item.save()
            messages.success(request, _('Our Team Created Successfully'), extra_tags='OurTeam')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontOurTeamList'))
        else:
            messages.error(request, _('Our Team Not Created'), extra_tags='OurTeam')
    else:
        block_form = AdminBlockForm()

    context = {'block': block_object, 'block_form': AdminBlockItemForm(), 'current_page': _('Our Team'),


               }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/team/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontOurTeamUpdate(request,slug):
    block_item = BlockItem.objects.get(slug=slug)
    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)

        if block_form:


            ######### images  block item ##########
            title = request.POST.get('title')
            keywords = request.POST.get('keywords')
            number = request.POST.get('number')
            email = request.POST.get('email')
            image = request.FILES.get('image')
            order = request.POST.get('order')
            status = request.POST.get('status')

            block_item_object = BlockItem.objects.get(id=block_item.id)
            block_item_object.title = title
            block_item_object.keywords = keywords
            block_item_object.number = number
            block_item_object.email = email
            if image:
                block_item_object.image = image

            block_item_object.order = order
            block_item_object.status = status

            block_item_object.save()

            messages.success(request, _("Our Team Add Successfully"), extra_tags='OurTeam')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontOurClientList'))
        else:

            messages.error(request, _("Our Team Not Add , Please Try Again"), extra_tags='OurTeam')
    else:
        context = {'block_item': block_item, 'block_form': AdminBlockForm(),

            'current_page': _('Update'), 'prev_Page': _('Our Clients'),
            'prev_Page_link': reverse_lazy('front:AdminFrontOurTeamList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/blocks/team/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontOurTeamDelete(request,slug):

    block_item = BlockItem.objects.get(slug=slug)

    block_item.delete()
    messages.success(request, _("Our Client Delete Successfully"), extra_tags='AboutPage')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontOurTeamList'))


##########################      Front Home Block   ################################


@authenticated_staff
@staff_only
def AdminFrontBlockHomeSliderList(request):
    sliders = Slider.objects.filter(type='HomeSlider')
    sliders_item = SliderItem.objects.filter(type='HomeSlider')
    context = {'sliders': sliders_item, 'slider_form': AdminSliderForm(), 'current_page': _('Slider'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/slider/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontBlockHomeSliderCreate(request):
    if request.method == "POST":
        slider_form = AdminSliderForm(request.POST or None, request.FILES or None)
        if slider_form:

            titles = request.POST.getlist('[title]')
            categories = request.POST.getlist('[category]')
            keywords = request.POST.getlist('[keywords]')
            urls = request.POST.getlist('[url]')
            images = request.FILES.getlist('[image]')


            try:
                slider_object = Slider.objects.get(type='HomeSlider')
            except:

                slider_object = Slider(title='HomeSlider',  type='HomeSlider',
                                        )
                slider_object.save()
            for title, category, keyword, url, image in zip( titles, categories, keywords, urls, images):
                if category == '' or category == None:
                    category = None
                else:
                    category = FrontCategories.objects.get(id=category)
                slider_item_object = SliderItem(title=title, category=category, keywords=keyword, url=url, image=image,
                                                type='HomeSlider')
                slider_item_object.save()

            messages.success(request, _("Slider Add Successfully"), extra_tags='Slider')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontBlockHomeSliderList'))
        else:

            messages.error(request, _("Slider Not Add , Please Try Again"), extra_tags='Slider')
    else:
        context = {'slider_form': AdminSliderForm(),

            'current_page': _('Add'), 'prev_Page': _('Slider'),
            'prev_Page_link': reverse_lazy('front:AdminFrontBlockHomeSliderList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/slider/add.html', context)

    context = {'slider_form': AdminSliderForm(),

        'current_page': _('Add'), 'prev_Page': _('Slider'),
        'prev_Page_link': reverse_lazy('front:AdminFrontSliderList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/slider/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontBlockHomeSliderUpdate(request, slug):
    slider = SliderItem.objects.get(slug=slug)

    if request.method == "POST":
        slider_form = AdminSliderItemForm(request.POST or None, request.FILES or None)

        if slider_form:
            title = request.POST.get('title')
            category = request.POST.get('category')
            keywords = request.POST.get('keywords')
            url = request.POST.get('url')
            image = request.FILES.get('image')
            status = request.POST.get('status')

            if category == '' or category == None:
                category = None
            else:
                category = FrontCategories.objects.get(id=category)

            slider_object = SliderItem.objects.get(slug=slug)
            slider_object.title = title
            slider_object.category = category
            slider_object.keywords = keywords
            slider_object.url = url
            if image:
                slider_object.image = image
            slider_object.status = status
            slider_object.save()



            messages.success(request, _("Slider Add Successfully"), extra_tags='Slider')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontBlockHomeSliderList'))
        else:

            messages.error(request, _("Slider Not Add , Please Try Again"), extra_tags='Slider')
    else:
        context = {'slider': slider,  'slider_form': AdminSliderItemForm(),

            'current_page': _('Update'), 'prev_Page': _('Slider'),
            'prev_Page_link': reverse_lazy('front:AdminFrontBlockHomeSliderList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/slider/update.html', context)

    context = {'slider': slider,  'slider_form': AdminSliderItemForm(),

        'current_page': _('Update'), 'prev_Page': _('Slider'),
        'prev_Page_link': reverse_lazy('front:AdminFrontSliderList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/slider/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontBlockHomeSliderDelete(request, slug):
    slider = SliderItem.objects.get(slug=slug)
    slider.delete()

    messages.success(request, _("Slider Delete Successfully"), extra_tags='Slider')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontBlockHomeSliderList'))


@authenticated_staff
@staff_only
def AdminFrontHomeAboutMainList(request):
    blocks = Block.objects.filter(type='HomeAboutMain')

    context = {'blocks': blocks, 'block_form': AdminBlockForm(), 'current_page': _('AboutMain'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/home/about/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontHomeAboutMainCreate(request):


    if request.method == 'POST':
        block_form = AdminBlockForm(request.POST, request.FILES)
        if block_form:
            title = request.POST.get('title')
            title2 = request.POST.get('title2')
            keywords = request.POST.get('keywords')
            category = request.POST.get('category')
            main_image = request.FILES.get('main_image')

            page = request.POST.get('page')

            section = request.POST.get('section')
            description = request.POST.get('description')

            ######### description  block item ##########
            creating_for = request.POST.get('creating_for')
            employee = request.POST.get('employee')

            ######### Number  block item ##########
            number_title_one = request.POST.get('number_title_one')
            number_description_one = request.POST.get('number_description_one')
            slider_order_one = request.POST.get('slider_order_one')

            number_title_two = request.POST.get('number_title_two')
            number_description_two = request.POST.get('number_description_two')
            slider_order_two = request.POST.get('slider_order_two')

            number_title_three = request.POST.get('number_title_three')
            number_title2_three = request.POST.get('number_title2_three')
            number_description_three = request.POST.get('number_description_three')
            slider_order_three = request.POST.get('slider_order_three')

            if category == '' or category == None:
                category = None
            else:
                category = FrontCategories.objects.get(id=category)
            if page == '' or page == None:
                page = None
            else:
                page = Pages.objects.get(id=page)

            try:
                block_object = Block.objects.get(type='HomeAboutMain')
                block_object.title = title
                block_object.title2 = title2
                block_object.keywords = keywords
                block_object.category = category
                block_object.page = page
                block_object.section = section
                block_object.description = description
                block_object.creating_for = creating_for
                block_object.employee = employee
                block_object.image = main_image
                block_object.save()
            except:

                block_object = Block(title=title,title2=title2, keywords=keywords, category=category, page=page, section=section,
                                     description=description, creating_for=creating_for, employee=employee,
                                     type='HomeAboutMain', image=main_image, order=0)
                block_object.save()



            ######### Number  block item ##########
            try:
                number_item_one = BlockItem.objects.get(block=block_object, creating_for='slider_order_one')
                number_item_one.title = number_title_one
                number_item_one.description = number_description_one
                number_item_one.order = slider_order_one
                number_item_one.save()
            except:
                number_item_one = BlockItem(block=block_object, title=number_title_one, description=number_description_one,
                                            type='Number', order=slider_order_one, creating_for='slider_order_one')
                number_item_one.save()

            try:
                number_item_two = BlockItem.objects.get(block=block_object, creating_for='slider_order_two')
                number_item_two.title = number_title_two
                number_item_two.description = number_description_two
                number_item_two.order = slider_order_two
                number_item_two.save()
            except:
                number_item_two = BlockItem(block=block_object, title=number_title_two, description=number_description_two,
                                            type='Number', order=slider_order_two, creating_for='slider_order_two')
                number_item_two.save()

            try:
                number_item_three = BlockItem.objects.get(block=block_object, creating_for='slider_order_three')
                number_item_three.title = number_title_three
                number_item_three.title2 = number_title2_three
                number_item_three.description = number_description_three
                number_item_three.order = slider_order_three
                number_item_three.save()
            except:
                number_item_three = BlockItem(block=block_object, title=number_title_three, itle2=number_title2_three,
                                              description=number_description_three,
                                            type='Number', order=slider_order_three, creating_for='slider_order_three')
                number_item_three.save()







            messages.success(request, _('AboutMain Created Successfully'), extra_tags='AboutMain')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontHomeAboutMainList'))
        else:
            messages.error(request, _('AboutMain Not Created'), extra_tags='AboutMain')

    else:
        block_form = AdminBlockForm()

    context = { 'block_form': AdminBlockForm(), 'current_page': _('AboutMain'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/home/about/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontHomeAboutMainUpdate(request, slug):
    blocks = Block.objects.get(slug=slug)
    block_item_one = BlockItem.objects.get(block=blocks, creating_for='slider_order_one')
    block_item_two = BlockItem.objects.get(block=blocks, creating_for='slider_order_two')
    block_item_three = BlockItem.objects.get(block=blocks, creating_for='slider_order_three')
    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)

        if block_form:
            title = request.POST.get('title')
            title2 = request.POST.get('title2')
            page = request.POST.get('page')
            section = request.POST.get('section')
            keywords =request.POST.get('keywords')
            description = request.POST.get('description')
            creating_for = request.POST.get('creating_for')
            employee = request.POST.get('employee')
            main_image = request.FILES.get('main_image')



            ######### Number  block item ##########
            number_title_one = request.POST.get('number_title_one')
            number_description_one = request.POST.get('number_description_one')
            slider_order_one = request.POST.get('slider_order_one')

            number_title_two = request.POST.get('number_title_two')
            number_description_two = request.POST.get('number_description_two')
            slider_order_two = request.POST.get('slider_order_two')

            number_title_three = request.POST.get('number_title_three')
            number_title2_three = request.POST.get('number_title2_three')
            number_description_three = request.POST.get('number_description_three')
            slider_order_three = request.POST.get('slider_order_three')

            ######### images  block item ##########
            item_title = request.POST.get('item_title')
            item_description = request.POST.get('item_description')
            item_images = request.FILES.get('item_images')

            block_object = Block.objects.get(slug=slug)
            block_object.title = title
            block_object.title2 = title2
            block_object.keywords=keywords
            block_object.page = page
            block_object.section = section
            block_object.description = description
            block_object.creating_for = creating_for
            block_object.employee = employee
            if main_image:
                block_object.image = main_image
            block_object.save()



            ######### Number  block item ##########
            number_item_one = BlockItem.objects.get(block=block_object, type='Number', creating_for='slider_order_one')
            number_item_one.title = number_title_one
            number_item_one.description = number_description_one
            number_item_one.order = slider_order_one
            number_item_one.save()

            number_item_two = BlockItem.objects.get(block=block_object, type='Number', creating_for='slider_order_two')
            number_item_two.title = number_title_two
            number_item_two.description = number_description_two
            number_item_two.order = slider_order_two
            number_item_two.save()


            number_item_three = BlockItem.objects.get(block=block_object, type='Number', creating_for='slider_order_three')
            number_item_three.title = number_title_three
            number_item_three.title2 = number_title2_three
            number_item_three.description = number_description_three
            number_item_three.order = slider_order_three
            number_item_three.save()



            messages.success(request, _("AboutMain Add Successfully"), extra_tags='AboutMain')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontHomeAboutMainList'))
        else:

            messages.error(request, _("AboutMain Not Add , Please Try Again"), extra_tags='AboutMain')

    context = {'blocks': blocks,
                'block_item_one': block_item_one,
                'block_item_two': block_item_two,
                'block_item_three': block_item_three,
               'block_form': AdminBlockForm(),

        'current_page': _('Update'), 'prev_Page': _('AboutMain'),
        'prev_Page_link': reverse_lazy('front:AdminFrontHomeAboutMainList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/home/about/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontHomeAboutMainDelete(request, slug):
    block = Block.objects.get(slug=slug)
    block_item = BlockItem.objects.filter(block=block)
    for item in block_item:
        item.delete()
    block.delete()

    messages.success(request, _("AboutMain Delete Successfully"), extra_tags='AboutMain')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontHomeAboutMainList'))



@authenticated_staff
@staff_only
def AdminFrontHomeSwiperList(request):
    blocks = BlockItem.objects.filter(type='HomeSwiper')
    if request.method == 'POST':
        title = request.POST.get('title')
        keywords = request.POST.get('keywords')
        keywords2 = request.POST.get('keywords2')

        try:
            block_object = Block.objects.get(type='HomeSwiper')
            block_object.title = title
            block_object.keywords2=keywords2
            block_object.keywords = keywords


            block_object.save()
        except:

            block_object = Block(title=title, keywords=keywords,keywords2=keywords2, type='HomeSwiper', order=0)
            block_object.save()

        messages.success(request, _('Swiper Created Successfully'), extra_tags='Swiper')
        return HttpResponseRedirect(reverse_lazy('front:AdminFrontHomeSwiperList'))


    context = {'blocks': blocks, 'block_form': AdminBlockForm(), 'current_page': _('Swiper'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/swiper/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontHomeSwiperCreate(request):
    if request.method == 'POST':
        block_form = AdminBlockForm(request.POST, request.FILES)
        if block_form:
            title = request.POST.get('title')
            keywords = request.POST.get('keywords')
            page = request.POST.get('page')
            order = request.POST.get('order')

            ######### images  block item ##########
            swiper_title = request.POST.getlist('[swiper_title]')
            swiper_description = request.POST.getlist('[swiper_description]')
            swiper_icon = request.FILES.getlist('[swiper_icon]')

            if page == '' or page == None:
                page = None
            else:
                page = Pages.objects.get(id=page)

            try:
                block_object = Block.objects.get(type='HomeSwiper')
                block_object.title = title
                block_object.keywords = keywords
                block_object.page = page
                block_object.order = order
                block_object.save()
            except:

                    block_object = Block(title=title, keywords=keywords, page=page, type='HomeSwiper', order=0)
                    block_object.save()

            ######### images  block item ##########
            for i in range(len(swiper_title)):
                block_item = BlockItem(block=block_object, title=swiper_title[i], description=swiper_description[i],
                                       image=swiper_icon[i], type='HomeSwiper', order=0)
                block_item.save()

            messages.success(request, _('Swiper Created Successfully'), extra_tags='Swiper')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontHomeSwiperList'))
        else:
            messages.error(request, _('Swiper Not Created'), extra_tags='Swiper')

    else:
        block_form = AdminBlockForm()
    context = {'block_form': block_form, 'current_page': _('Swiper'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/swiper/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontHomeSwiperUpdate(request, slug):
    block_item = BlockItem.objects.get(slug=slug)

    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)

        if block_form:

            ######### images  block item ##########
            swiper_title = request.POST.get('swiper_title')
            swiper_description = request.POST.get('swiper_description')
            swiper_icon = request.FILES.get('swiper_icon')
            order = request.POST.get('order')

            block_item_object = BlockItem.objects.get(slug=slug)
            block_item_object.title = swiper_title
            block_item_object.description = swiper_description
            if swiper_icon:
                block_item_object.image = swiper_icon
            block_item_object.order = order
            block_item_object.save()
            messages.success(request, _("Swiper Add Successfully"), extra_tags='Swiper')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontHomeSwiperList'))
        else:

         messages.error(request, _("Swiper Not Add , Please Try Again"), extra_tags='Swiper')
    else:
        context = {'block_item': block_item,  'block_form': AdminBlockForm(),
            'current_page': _('Update'), 'prev_Page': _('Swiper'),
            'prev_Page_link': reverse_lazy('front:AdminFrontHomeSwiperList'),}
        return render(request, f'{BACKEND_TEMPLATES}/front/blocks/swiper/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontHomeSwiperDelete(request, slug):
    block = BlockItem.objects.get(slug=slug)

    block.delete()

    messages.success(request, _("Swiper Delete Successfully"), extra_tags='Swiper')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontSwiperList'))



@authenticated_staff
@staff_only
def AdminFrontHomeHeroMainList(request):
    blocks = Block.objects.filter(type='HomeHero')

    context = {'blocks': blocks, 'block_form': AdminBlockForm(), 'current_page': _('HeroMain'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/home/hero/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontHomeHeroMainCreate(request):
    blocks = Block.objects.filter(type='HomeHero')
    if request.method == 'POST':
        block_form = AdminBlockForm(request.POST, request.FILES)
        if block_form:

            keywords = request.POST.get('keywords')
            category = request.POST.get('category')
            page = request.POST.get('page')
            section = request.POST.get('section')

            ######### images  block item ##########
            item_title = request.POST.get('item_title')
            item_keywords = request.POST.get('item_keywords')
            item_description = request.POST.get('item_description')
            main_image = request.FILES.get('main_image')
            main_gif = request.FILES.get('main_gif')
            video = request.FILES.get('video')
            item_url = request.POST.get('item_url')
            item_order = request.POST.get('item_order')
            item_video_url = request.POST.get('item_video_url')
            item_video_id = request.POST.get('item_video_id')

            if category == '' or category == None:
                category = None
            else:
                category = FrontCategories.objects.get(id=category)

            if page == '' or page == None:
                page = None
            else:
                page = Pages.objects.get(id=page)
            # title = title + ' ' + str(page)
            title = 'About Hero'

            try:
                block_object = Block.objects.get(type='HomeHero')
            except:
                block_object = Block(title=title, keywords=keywords, category=category, page=page, section=section,
                                      type='HomeHero', order=0)
                block_object.save()

            # block_object.refresh_from_db()

            ######### images  block item ##########
            try:
                block_item = BlockItem.objects.get(block=block_object, type='HomeHero')
                block_item.title = item_title
                block_item.keywords = item_keywords
                block_item.description = item_description
                block_item.image = main_image
                block_item.gif = main_gif
                block_item.video = video

                block_item.url = item_url
                block_item.order = item_order
                block_item.video_url = item_video_url
                block_item.save()
            except:


                block_item = BlockItem(block=block_object,  title=item_title, keywords=item_keywords,
                                       description=item_description, image=main_image,gif=main_gif,
                                       video=video, url=item_url,
                                       order=item_order,
                                       video_url=item_video_url,video_id=item_video_id,
                                       type='HomeHero')
                block_item.save()

            messages.success(request, _('About Hero Created Successfully'), extra_tags='AboutPage')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontHomeHeroMainList'))
        else:
            messages.error(request, _('About Hero Not Created'), extra_tags='AboutPage')

    else:
        block_form = AdminBlockForm()

    context = {'blocks': blocks, 'block_form': AdminBlockForm(), 'current_page': _('AboutHero'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/home/hero/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontHomeHeroMainUpdate(request, slug):
    blocks = Block.objects.get(slug=slug)
    block_item = BlockItem.objects.get(block=blocks)
    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)

        if block_form:
            title = request.POST.get('title')
            page = request.POST.get('page')
            order = request.POST.get('order')

            ######### images  block item ##########
            item_title = request.POST.get('item_title')
            item_keywords = request.POST.get('item_keywords')
            item_description = request.POST.get('item_description')
            main_image = request.FILES.get('main_image')
            main_gif = request.FILES.get('main_gif')
            video = request.FILES.get('video')
            item_url = request.POST.get('item_url')
            item_order = request.POST.get('item_order')
            item_video_url = request.POST.get('item_video_url')
            item_video_id = request.POST.get('item_video_id')



            ######### images  block item ##########
            block_item = BlockItem.objects.get(block=blocks, type='HomeHero')
            block_item.title = item_title
            block_item.keywords = item_keywords
            block_item.description = item_description

            if main_image:
                block_item.image = main_image
            if video:
                block_item.video = video
            if main_gif:
                block_item.gif = main_gif
            block_item.url = item_url
            block_item.order = item_order
            block_item.video_url = item_video_url
            block_item.video_id = item_video_id

            block_item.save()

            messages.success(request, _("About Hero Add Successfully"), extra_tags='HomePage')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontHomeHeroMainList'))
        else:

            messages.error(request, _("About Hero Not Add , Please Try Again"), extra_tags='HomePage')
    else:
        context = {'blocks': blocks, 'block_item': block_item, 'block_form': AdminBlockForm(),

            'current_page': _('Update'), 'prev_Page': _('AboutHero'),
            'prev_Page_link': reverse_lazy('front:AdminFrontHomeHeroMainList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/blocks/home/hero/update.html', context)

    context = {'blocks': blocks, 'block_item': block_item, 'block_form': AdminBlockForm(),

        'current_page': _('Update'), 'prev_Page': _('AboutHero'),
        'prev_Page_link': reverse_lazy('front:AdminFrontHomeHeroMainList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/home/hero/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontHomeHeroMainDelete(request, slug):
    block = Block.objects.get(slug=slug)
    block_item = BlockItem.objects.filter(block=block)
    for item in block_item:
        item.delete()
    block.delete()

    messages.success(request, _("About Hero Delete Successfully"), extra_tags='HomePage')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontHomeHeroMainList'))

@authenticated_staff
@staff_only
def AdminFrontHomeHeroMainDeleteVideoFromUpdate(request,slug):
    block = BlockItem.objects.get(slug=slug)
    if request.method == "POST":
       try:
           if block.video:
               block.video.delete()
               block.video = None
               block.save()
               messages.success(request, _("Video Delete Successfully"), extra_tags='HomePage')
               return redirect(request.META['HTTP_REFERER'])
       except Exception as e:
           messages.error(request, _(f"Video Not Delete Reason {e}"), extra_tags='HomePage')
    # block.video = None
    # block.save()
    return redirect(request.META['HTTP_REFERER'])

##########################      Front Portfolio   ################################

@authenticated_staff
@staff_only
def AdminFrontPortfolioList(request):
    blocks = Block.objects.filter(type='Portfolio')
    if request.method == 'POST':
        title = request.POST.get('title')
        keywords = request.POST.get('keywords')
        keywords2 = request.POST.get('keywords2')

        try:
            block_object = Block.objects.get(type='PortfolioBlock')
            block_object.title = title
            block_object.keywords2 = keywords2
            block_object.keywords = keywords
            block_object.save()
        except:

            block_object = Block(title=title, keywords=keywords, keywords2=keywords2, type='PortfolioBlock', order=0)
            block_object.save()

        messages.success(request, _('Swiper Created Successfully'), extra_tags='Swiper')
        return HttpResponseRedirect(reverse_lazy('front:AdminFrontHomeSwiperList'))


    context = {'blocks': blocks, 'block_form': AdminBlockForm(), 'current_page': _('Portfolio'),

               }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/portfolio/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontPortfolioCreate(request):
    if request.method == 'POST':
        block_form = AdminBlockForm(request.POST, request.FILES)
        if block_form:
            title = request.POST.get('title')
            keywords = request.POST.get('keywords')
            category = request.POST.get('category')
            page_style = request.POST.get('page_style')
            main_image = request.FILES.get('main_image')
            show_on_home = request.POST.get('show_on_home')

            page = request.POST.get('page')
            order = request.POST.get('order')
            section = request.POST.get('section')
            description = request.POST.get('description')
            image_url = request.POST.get('image_url')

            ############  block item ############
            slider_order = request.POST.getlist('slider_order')

            ######### description  block item ##########
            creating_for = request.POST.get('creating_for')
            employee = request.POST.get('employee')
            published_at = request.POST.get('published_at')
            description_url = request.POST.get('description_url')
            description_description = request.POST.get('description_description')
            description_keywords = request.POST.get('description_keywords')

            ######### media  block item ##########
            video_url = request.POST.get('video_url')
            video_cover = request.FILES.get('video_cover')
            ######### images  block item ##########
            slider_title1 = request.POST.get('slider_title1')
            slider_image1 = request.FILES.get('slider_image1')
            slider_title2 = request.POST.get('slider_title2')
            slider_image2 = request.FILES.get('slider_image2')
            slider_title3 = request.POST.get('slider_title3')
            slider_image3 = request.FILES.get('slider_image3')
            slider_title4 = request.POST.get('slider_title4')
            slider_image4 = request.FILES.get('slider_image4')
            slider_title5 = request.POST.get('slider_title5')
            slider_image5 = request.FILES.get('slider_image5')
            slider_title6 = request.POST.get('slider_title6')
            slider_image6 = request.FILES.get('slider_image6')
            slider_title7 = request.POST.get('slider_title7')
            slider_image7 = request.FILES.get('slider_image7')

            ############## About Card  Block Item ##############
            about_title = request.POST.get('about_title')
            about_url = request.POST.get('about_url')
            about_images = request.FILES.get('about_images')
            about_description = request.POST.get('about_description')

            if category == '' or category == None:
                category = None
            else:
                category = FrontCategories.objects.get(id=category)



            if page == '' or page == None:
                page = None
            else:
                page = Pages.objects.get(id=page)

            if published_at == '' or published_at == None:
                published_at = datetime.now().strftime("%Y-%m-%d")

            # get_last_portfolio = Block.objects.filter(type='Portfolio').last()
            # if get_last_portfolio:
            #     port_number = get_last_portfolio.order + 1
            # else:
            #     port_number = 1

            try:
                get_last_portfolio = Block.objects.filter(type='Portfolio').last()
                port_number = get_last_portfolio.number + 1
            except:
                port_number = 1


            block_object = Block(title=title, keywords=keywords, category=category, page_style=page_style,show_on_home=show_on_home,
                                 image=main_image, page=page, section=section, description=description,
                                 image_url=image_url, type='Portfolio', order=0,number=port_number)
            block_object.save()


            ######### description  block item ##########
            try:
                description_item = BlockItem.objects.get(block=block_object, type='Info')
                description_item.creating_for = creating_for
                description_item.employee = employee
                description_item.url = description_url
                description_item.published_at = published_at
                description_item.description = description_description
                description_item.keywords = description_keywords
                description_item.save()
            except:
                description_item = BlockItem(block=block_object, creating_for=creating_for, employee=employee,
                                            url=description_url, published_at=published_at, description=description_description,
                                            keywords=description_keywords,
                                            type='Info', order=0)
                description_item.save()

            ######### media  block item ##########
            try:
                media_item = BlockItem.objects.get(block=block_object, type='Video')
                media_item.video_url = video_url
                media_item.video_cover = video_cover
                media_item.save()
            except:
                media_item = BlockItem(block=block_object, video_url=video_url, video_cover=video_cover, type='Video',
                                       order=0)
                media_item.save()

            ######### images  block item ##########
            block_item1 = BlockItem(block=block_object, title=slider_title1, image=slider_image1, type='Images',
                                   order=1, number=1)
            block_item1.save()
            block_item2 = BlockItem(block=block_object, title=slider_title2, image=slider_image2, type='Images',
                                      order=2, number=2)
            block_item2.save()
            block_item3 = BlockItem(block=block_object, title=slider_title3, image=slider_image3, type='Images',
                                        order=3, number=3)
            block_item3.save()
            block_item4 = BlockItem(block=block_object, title=slider_title4, image=slider_image4, type='Images',
                                        order=4, number=4)
            block_item4.save()
            block_item5 = BlockItem(block=block_object, title=slider_title5, image=slider_image5, type='Images',
                                        order=5, number=5)
            block_item5.save()
            block_item6 = BlockItem(block=block_object, title=slider_title6, image=slider_image6, type='Images',
                                        order=6, number=6)
            block_item6.save()
            block_item7 = BlockItem(block=block_object, title=slider_title7, image=slider_image7, type='Images',
                                        order=7, number=7)
            block_item7.save()

            ############## About Card  Block Item ##############
            try:
                about_item = BlockItem.objects.get(block=block_object, type='AboutCard')
                about_item.title = about_title
                about_item.url = about_url
                about_item.image = about_images
                about_item.description = about_description
                about_item.save()
            except:
                about_item = BlockItem(block=block_object, title=about_title, url=about_url, image=about_images,
                                       description=about_description, type='AboutCard', order=7)
                about_item.save()

            messages.success(request, _('Portfolio Created Successfully'), extra_tags='Portfolio')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontPortfolioList'))
        else:
            messages.error(request, _('Portfolio Not Created'), extra_tags='Portfolio')

    else:
        block_form = AdminBlockForm()
    context = {'block_form': block_form, 'current_page': _('Portfolio'), }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/portfolio/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontPortfolioUpdate(request, slug):
    blocks = Block.objects.get(slug=slug)
    block_item = BlockItem.objects.filter(block=blocks)
    description_item = BlockItem.objects.filter(block=blocks, type='Info').last()
    media_item = BlockItem.objects.get(block=blocks, type='Video')
    about_item = BlockItem.objects.get(block=blocks, type='AboutCard')
    images_item1 = BlockItem.objects.get(block=blocks, type='Images' , number=1, order=1)
    images_item2 = BlockItem.objects.get(block=blocks, type='Images' , number=2, order=2)
    images_item3 = BlockItem.objects.get(block=blocks, type='Images' , number=3, order=3)
    images_item4 = BlockItem.objects.get(block=blocks, type='Images' , number=4, order=4)
    images_item5 = BlockItem.objects.get(block=blocks, type='Images' , number=5, order=5)
    images_item6 = BlockItem.objects.get(block=blocks, type='Images' , number=6, order=6)
    images_item7 = BlockItem.objects.get(block=blocks, type='Images' , number=7, order=7)
    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)

        if block_form:
            title = request.POST.get('title')
            keywords = request.POST.get('keywords')
            category = request.POST.get('category')
            page_style = request.POST.get('page_style')
            main_image = request.FILES.get('main_image')
            show_on_home = request.POST.get('show_on_home')

            page = request.POST.get('page')
            order = request.POST.get('order')
            section = request.POST.get('section')
            description = request.POST.get('description')
            image_url = request.POST.get('image_url')

            ############  block item ############
            slider_order = request.POST.getlist('slider_order')

            ######### description  block item ##########
            creating_for = request.POST.get('creating_for')
            employee = request.POST.get('employee')
            published_at = request.POST.get('published_at')
            description_url = request.POST.get('description_url')
            description_keywords = request.POST.get('description_keywords')
            description_description = request.POST.get('description_description')

            ######### media  block item ##########
            video_url = request.POST.get('video_url')
            video_cover = request.FILES.get('video_cover')
            ######### images  block item ##########
            slider_title1 = request.POST.get('slider_title1')
            slider_image1 = request.FILES.get('slider_image1')
            slider_title2 = request.POST.get('slider_title2')
            slider_image2 = request.FILES.get('slider_image2')
            slider_title3 = request.POST.get('slider_title3')
            slider_image3 = request.FILES.get('slider_image3')
            slider_title4 = request.POST.get('slider_title4')
            slider_image4 = request.FILES.get('slider_image4')
            slider_title5 = request.POST.get('slider_title5')
            slider_image5 = request.FILES.get('slider_image5')
            slider_title6 = request.POST.get('slider_title6')
            slider_image6 = request.FILES.get('slider_image6')
            slider_title7 = request.POST.get('slider_title7')
            slider_image7 = request.FILES.get('slider_image7')

            ############## About Card  Block Item ##############
            about_title = request.POST.get('about_title')
            about_url = request.POST.get('about_url')
            about_images = request.FILES.get('about_images')
            about_description = request.POST.get('about_description')

            if category == '' or category == None:
                category = None
            else:
                category = FrontCategories.objects.get(id=category)




            block_object = Block.objects.get(slug=slug)
            block_object.title = title
            block_object.keywords = keywords
            block_object.category = category
            block_object.page_style = page_style
            if main_image:
                block_object.image = main_image
            block_object.page = page
            block_object.section = section
            block_object.description = description
            block_object.image_url = image_url
            block_object.show_on_home = show_on_home
            block_object.save()
            # block_object.refresh_from_db()
            ######### description
            description_item_object = BlockItem.objects.filter(block=block_object, type='Info').last()
            description_item_object.creating_for = creating_for
            description_item_object.employee = employee
            description_item_object.url = description_url
            if published_at != '':
                description_item_object.published_at = published_at
            description_item_object.description = description_description
            description_item_object.keywords = description_keywords
            description_item_object.save()

            ######### media  block item ##########
            media_item_object = BlockItem.objects.get(block=block_object, type='Video')
            media_item_object.video_url = video_url
            media_item_object.video_cover = video_cover
            media_item_object.save()

            ######### images  block item ##########
            try:
                images_item_object = BlockItem.objects.get(block=block_object, type='Images', number=1, order=1)
                images_item_object.title = slider_title1
                if slider_image1:
                    images_item_object.image = slider_image1
                images_item_object.order = 1
                images_item_object.number = 1
                images_item_object.save()
            except:
                images_item_object = BlockItem(block=block_object, title=slider_title1, image=slider_image1, type='Images',
                                        order=1, number=1)
                images_item_object.save()

            try:
                images_item_object = BlockItem.objects.get(block=block_object, type='Images', number=2, order=2)
                images_item_object.title = slider_title2
                if slider_image2:
                    images_item_object.image = slider_image2

                images_item_object.order = 2
                images_item_object.number = 2
                images_item_object.save()

            except:
                images_item_object = BlockItem(block=block_object, title=slider_title2, image=slider_image2, type='Images',
                                        order=2, number=2)
                images_item_object.save()

            try:
                images_item_object = BlockItem.objects.get(block=block_object, type='Images', number=3, order=3)
                images_item_object.title = slider_title3
                if slider_image3:
                 images_item_object.image = slider_image3
                images_item_object.order = 3
                images_item_object.number = 3
                images_item_object.save()
            except:
                images_item_object = BlockItem(block=block_object, title=slider_title3, image=slider_image3, type='Images',
                                        order=3, number=3)
                images_item_object.save()

            try:
                images_item_object = BlockItem.objects.get(block=block_object, type='Images', number=4, order=4)
                images_item_object.title = slider_title4
                if slider_image4:
                    images_item_object.image = slider_image4
                images_item_object.order = 4
                images_item_object.number = 4
                images_item_object.save()
            except:
                images_item_object = BlockItem(block=block_object, title=slider_title4, image=slider_image4, type='Images',
                                        order=4, number=4)
                images_item_object.save()

            try:
                images_item_object = BlockItem.objects.get(block=block_object, type='Images', number=5, order=5)
                images_item_object.title = slider_title5
                if slider_image5:
                    images_item_object.image = slider_image5
                images_item_object.order = 5
                images_item_object.number = 5
                images_item_object.save()
            except:
                images_item_object = BlockItem(block=block_object, title=slider_title5, image=slider_image5, type='Images',
                                        order=5, number=5)
                images_item_object.save()

            try:
                images_item_object = BlockItem.objects.get(block=block_object, type='Images', number=6, order=6)
                images_item_object.title = slider_title6
                if slider_image6:
                    images_item_object.image = slider_image6
                images_item_object.order = 6
                images_item_object.number = 6
                images_item_object.save()
            except:
                images_item_object = BlockItem(block=block_object, title=slider_title6, image=slider_image6, type='Images',
                                        order=6, number=6)
                images_item_object.save()

            try:
                images_item_object = BlockItem.objects.get(block=block_object, type='Images', number=7, order=7)
                images_item_object.title = slider_title7
                if slider_image7:
                    images_item_object.image = slider_image7
                images_item_object.order = 7
                images_item_object.number = 7
                images_item_object.save()
            except:
                images_item_object = BlockItem(block=block_object, title=slider_title7, image=slider_image7, type='Images',
                                        order=7, number=7)
                images_item_object.save()




            ############## About Card  Block Item ##############
            about_item = BlockItem.objects.get(block=block_object, type='AboutCard')
            about_item.title = about_title
            about_item.url = about_url
            if about_images:
                about_item.image = about_images
            about_item.description = about_description
            about_item.save()

            messages.success(request, _("Portfolio Add Successfully"), extra_tags='Portfolio')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontPortfolioList'))
        else:

                messages.error(request, _("Portfolio Not Add , Please Try Again"), extra_tags='Portfolio')



    context = {'blocks': blocks,
               'description_item': description_item, 'media_item': media_item, 'about_item': about_item,
                'images_item1': images_item1, 'images_item2': images_item2, 'images_item3': images_item3,
                'images_item4': images_item4, 'images_item5': images_item5, 'images_item6': images_item6,
                'images_item7': images_item7,
               'block_item': block_item, 'block_form': AdminBlockForm(),

                    'current_page': _('Update'), 'prev_Page': _('Portfolio'),
                    'prev_Page_link': reverse_lazy('front:AdminFrontPortfolioList'),

                }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/portfolio/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontPortfolioDelete(request, slug):
    block = Block.objects.get(slug=slug)
    block_item = BlockItem.objects.filter(block=block)
    for item in block_item:
        item.delete()
    block.delete()

    messages.success(request, _("Portfolio Delete Successfully"), extra_tags='Portfolio')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontPortfolioList'))








################### Front Block About #############################
@authenticated_staff
@staff_only
def AdminFrontPageAboutHeroList(request):
    blocks = Block.objects.filter(type='AboutHero')
    block_item = BlockItem.objects.filter(block=Block.objects.get(type='AboutHero'))

    context = {'blocks': block_item, 'block_form': AdminBlockForm(), 'current_page': _('AboutHero'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/hero/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontPageAboutHeroCreate(request):
    blocks = Block.objects.filter(type='AboutHero')
    if request.method == 'POST':
        block_form = AdminBlockForm(request.POST, request.FILES)

        if block_form:

            keywords = request.POST.get('keywords')
            category = request.POST.get('category')

            page = request.POST.get('page')

            section = request.POST.get('section')
            description = request.POST.get('description')

            ######### images  block item ##########
            item_title = request.POST.get('item_title')
            item_keywords = request.POST.get('item_keywords')
            item_description = request.POST.get('item_description')
            main_image = request.FILES.get('main_image')
            item_url = request.POST.get('item_url')
            item_order = request.POST.get('item_order')
            item_video_url = request.POST.get('item_video_url')

            if category == '' or category == None:
                category = None
            else:
                category = FrontCategories.objects.get(id=category)

            if page == '' or page == None:
                page = None
            else:
                page = Pages.objects.get(id=page)

            title = 'About Hero'

            try:
                block_object = Block.objects.get(type='AboutHero')
            except:
                block_object = Block(title=title, keywords=keywords, category=category, page=page, section=section,
                                     description=description, type='AboutHero', order=0)
                block_object.save()

            # block_object.refresh_from_db()

            ######### images  block item ##########
            try:
                block_item = BlockItem.objects.get(block=block_object, type='AboutHero')
                block_item.title = item_title
                block_item.keywords = item_keywords
                block_item.description = item_description
                if main_image != None or main_image != '':
                    block_item.image = main_image
                block_item.url = item_url
                block_item.order = item_order
                block_item.video_url = item_video_url
                block_item.save()
            except:

                block_item = BlockItem(block=block_object,  title=item_title, keywords=item_keywords,
                                       description=item_description, image=main_image, url=item_url, order=item_order,
                                       video_url=item_video_url,type='AboutHero')
                block_item.save()

            messages.success(request, _('About Hero Created Successfully'), extra_tags='AboutPage')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontPageAboutHeroList'))
        else:
            messages.error(request, _('About Hero Not Created'), extra_tags='AboutPage')

    else:
        block_form = AdminBlockForm()

    context = {'blocks': blocks, 'block_form': AdminBlockForm(), 'current_page': _('AboutHero'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/hero/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontPageAboutHeroUpdate(request, slug):
    blocks = Block.objects.get(slug=slug)
    block_item = BlockItem.objects.get(block=blocks)
    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)

        if block_form:
            title = request.POST.get('title')
            page = request.POST.get('page')
            order = request.POST.get('order')

            ######### images  block item ##########
            item_title = request.POST.get('item_title')
            item_keywords = request.POST.get('item_keywords')
            item_description = request.POST.get('item_description')
            main_image = request.FILES.get('main_image')
            item_url = request.POST.get('item_url')
            item_order = request.POST.get('item_order')
            item_video_url = request.POST.get('item_video_url')

            block_object = Block.objects.get(slug=slug)
            block_object.title = title
            block_object.page = page
            block_object.order = order
            block_object.save()

            ######### images  block item ##########
            block_item = BlockItem.objects.get(block=block_object, type='AboutHero')
            block_item.title = item_title
            block_item.keywords = item_keywords
            block_item.description = item_description
            if main_image:
                block_item.image = main_image
            block_item.url = item_url
            block_item.order = item_order
            block_item.video_url = item_video_url
            block_item.save()

            messages.success(request, _("About Hero Add Successfully"), extra_tags='AboutPage')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontPageAboutHeroList'))
        else:

            messages.error(request, _("About Hero Not Add , Please Try Again"), extra_tags='AboutPage')
    else:
        context = {'blocks': blocks, 'block_item': block_item, 'block_form': AdminBlockForm(),

            'current_page': _('Update'), 'prev_Page': _('AboutHero'),
            'prev_Page_link': reverse_lazy('front:AdminFrontPageAboutHeroList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/hero/update.html', context)

    context = {'blocks': blocks, 'block_item': block_item, 'block_form': AdminBlockForm(),

        'current_page': _('Update'), 'prev_Page': _('AboutHero'),
        'prev_Page_link': reverse_lazy('front:AdminFrontPageAboutHeroList'),

    }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/hero/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontPageAboutHeroDelete(request, slug):
    block = Block.objects.get(slug=slug)
    block_item = BlockItem.objects.filter(block=block)
    for item in block_item:
        item.delete()
    block.delete()

    messages.success(request, _("About Hero Delete Successfully"), extra_tags='AboutPage')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontPageAboutHeroList'))


################### Front Block About #############################
@authenticated_staff
@staff_only
def AdminFrontPageAboutCvList(request):
    blocks = Block.objects.filter(type='AboutCv')

    context = {'blocks': blocks, 'block_form': AdminBlockForm(), 'current_page': _('AboutCv'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/cv/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontPageAboutCvCreate(request):
    blocks = Block.objects.filter(type='AboutCv')
    if request.method == 'POST':
        block_form = AdminBlockForm(request.POST, request.FILES)
        if block_form:
            title = request.POST.get('title')
            keywords = request.POST.get('keywords')
            category = request.POST.get('category')

            page = request.POST.get('page')
            order = request.POST.get('order')
            section = request.POST.get('section')
            description = request.POST.get('description')

            ######### images  block item ##########
            item_title = request.POST.get('item_title')
            item_keywords = request.POST.get('item_keywords')
            item_keywords2 = request.POST.get('item_keywords2')
            item_description = request.POST.get('item_description')
            main_image = request.FILES.get('main_image')
            item_url = request.POST.get('item_url')
            item_pdf = request.FILES.get('item_pdf')
            item_number = request.POST.get('item_number')
            item_residence = request.POST.get('item_residence')
            item_address = request.POST.get('item_address')
            item_email = request.POST.get('item_email')
            item_order = request.POST.get('item_order')

            if category == '' or category == None:
                category = None
            else:
                category = FrontCategories.objects.get(id=category)

            if page == '' or page == None:
                page = None
            else:
                page = Pages.objects.get(id=page)

            # title = title + ' ' + str(page)
            title = 'About Cv'

            try:
                block_object = Block.objects.get(type='AboutCv')
            except:
                block_object = Block(title=title, keywords=keywords, category=category, page=page, section=section,
                                     description=description, type='AboutCv', order=0)
                block_object.save()

            # block_object.refresh_from_db()

            ######### images  block item ##########
            try:
                block_item = BlockItem.objects.get(block=block_object, type='Images')
                block_item.title = item_title
                block_item.keywords = item_keywords
                block_item.keywords2 = item_keywords2
                block_item.description = item_description
                block_item.image = main_image
                block_item.url = item_url
                block_item.pdf = item_pdf
                block_item.number = item_number
                block_item.residence = item_residence
                block_item.address = item_address
                block_item.email = item_email
                block_item.order = item_order
                block_item.save()
            except:


                block_item = BlockItem(block=block_object, type='Images', title=item_title, keywords=item_keywords,
                                       keywords2=item_keywords2, description=item_description, image=main_image,
                                       url=item_url, pdf=item_pdf, number=item_number, residence=item_residence,
                                       address=item_address, email=item_email, order=item_order)
                block_item.save()

            messages.success(request, _('About Cv Created Successfully'), extra_tags='AboutPage')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontPageAboutCvList'))
        else:
            messages.error(request, _('About Cv Not Created'), extra_tags='AboutPage')

    else:
        block_form = AdminBlockForm()

    context = {'blocks': blocks, 'block_form': AdminBlockForm(), 'current_page': _('AboutCv'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/cv/add.html', context)

@authenticated_staff
@staff_only
def AdminFrontPageAboutCvUpdate(request, slug):
    blocks = Block.objects.get(slug=slug)
    block_item = BlockItem.objects.get(block=blocks)
    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)

        if block_form:
            title = request.POST.get('title')
            page = request.POST.get('page')
            order = request.POST.get('order')

            ######### images  block item ##########
            item_title = request.POST.get('item_title')
            item_keywords = request.POST.get('item_keywords')
            item_keywords2 = request.POST.get('item_keywords2')
            item_description = request.POST.get('item_description')
            main_image = request.FILES.get('main_image')
            item_url = request.POST.get('item_url')
            item_pdf = request.FILES.get('item_pdf')
            item_number = request.POST.get('item_number')
            item_residence = request.POST.get('item_residence')
            item_address = request.POST.get('item_address')
            item_email = request.POST.get('item_email')
            item_order = request.POST.get('item_order')

            block_object = Block.objects.get(slug=slug)
            block_object.title = title
            block_object.page = page
            block_object.order = order
            block_object.save()

            ######### images  block item ##########
            block_item = BlockItem.objects.get(block=block_object, type='Images')
            block_item.title = item_title
            block_item.keywords = item_keywords
            block_item.keywords2 = item_keywords2
            block_item.description = item_description
            if main_image:
                 block_item.image = main_image
            block_item.url = item_url
            block_item.pdf = item_pdf
            block_item.number = item_number
            block_item.residence = item_residence
            block_item.address = item_address
            block_item.email = item_email
            block_item.order = item_order
            block_item.save()

            messages.success(request, _("About Cv Add Successfully"), extra_tags='AboutPage')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontPageAboutCvList'))
        else:

            messages.error(request, _("About Cv Not Add , Please Try Again"), extra_tags='AboutPage')
    else:
        context = {'blocks': blocks, 'block_item': block_item, 'block_form': AdminBlockForm(),

            'current_page': _('Update'), 'prev_Page': _('AboutCv'),
            'prev_Page_link': reverse_lazy('front:AdminFrontPageAboutCvList'),

        }
        return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/cv/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontPageAboutCvDelete(request, slug):
    block = Block.objects.get(slug=slug)
    block_item = BlockItem.objects.filter(block=block)
    block.delete()
    block_item.delete()
    messages.success(request, _("About Cv Delete Successfully"), extra_tags='AboutPage')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontPageAboutCvList'))


################### Front Block About #############################
@authenticated_staff
@staff_only
def AdminFrontPageAboutResumeList(request):
    try:
       blocks = Block.objects.get(type='AboutResume')
    except:
        blocks = None
    block_item = BlockItem.objects.filter(block=blocks)


    context = {'blocks': block_item, 'block_form': AdminBlockForm(), 'current_page': _('AboutResume'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/resume/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontPageAboutResumeCreate(request):
    blocks = BlockItem.objects.filter(type='AboutResume')
    if request.method == 'POST':
        block_form = AdminBlockForm(request.POST, request.FILES)
        if block_form:
            title = request.POST.get('title')
            keywords = request.POST.get('keywords')
            category = request.POST.get('category')

            page = request.POST.get('page')
            order = request.POST.get('order')
            section = request.POST.get('section')
            description = request.POST.get('description')

            ######### education  block item ##########
            education_title = request.POST.getlist('[education_title]')
            education_description = request.POST.getlist('[education_description]')

            ######### experience  block item ##########
            experience_title = request.POST.getlist('[experience_title]')
            experience_description = request.POST.getlist('[experience_description]')

            if category == '' or category == None:
                category = None
            else:
                category = FrontCategories.objects.get(id=category)

            if page == '' or page == None:
                page = None
            else:
                page = Pages.objects.get(id=page)

            try:
                block_object = Block.objects.get(type='AboutResume')
            except:
                block_object = Block(title=title, keywords=keywords, category=category, page=page, section=section,
                                     description=description, type='AboutResume', order=0)
                block_object.save()

            ######### education  block item ##########
            for i in range(len(education_title)):
                block_item = BlockItem(block=block_object, type='Education', title=education_title[i],
                                       description=education_description[i], order=i)
                block_item.save()

            ######### experience  block item ##########
            for i in range(len(experience_title)):
                block_item = BlockItem(block=block_object, type='Experience', title=experience_title[i],
                                       description=experience_description[i], order=i)
                block_item.save()

            messages.success(request, _('About Resume Created Successfully'), extra_tags='AboutPage')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontPageAboutResumeList'))
        else:
            messages.error(request, _('About Resume Not Created'), extra_tags='AboutPage')

    else:
        block_form = AdminBlockForm()

    context = {'blocks': blocks, 'block_form': AdminBlockForm(), 'current_page': _('AboutResume'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/resume/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontPageAboutResumeUpdate(request, slug):
    blocks = BlockItem.objects.get(slug=slug)

    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)

        if block_form:
            title = request.POST.get('title')
            description = request.POST.get('description')
            order = request.POST.get('order')

            block_object = BlockItem.objects.get(slug=slug)
            block_object.title = title
            block_object.description = description
            block_object.order = order
            block_object.save()



            messages.success(request, _("About Resume Add Successfully"), extra_tags='AboutPage')

            return HttpResponseRedirect(reverse_lazy('front:AdminFrontPageAboutResumeList'))
        else:

            messages.error(request, _("About Resume Not Add , Please Try Again"), extra_tags='AboutPage')


    context = {'blocks': blocks,  'block_form': AdminBlockForm(),

        'current_page': _('Update'), 'prev_Page': _('AboutResume'),
        'prev_Page_link': reverse_lazy('front:AdminFrontPageAboutResumeList')
               }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/resume/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontPageAboutResumeDelete(request, slug):
    block = BlockItem.objects.get(slug=slug)
    block.delete()
    messages.success(request, _("About Resume Delete Successfully"), extra_tags='AboutPage')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontPageAboutResumeList'))


################### Front Block About #############################
@authenticated_staff
@staff_only
def AdminFrontPageAboutExperienceList(request):
    try:
       blocks = Block.objects.filter(type='AboutExperience')
    except:
        blocks = None
    check_block = Block.objects.filter(type='AboutExperience').last()


    context = {'blocks': blocks,
                'check_block_item': check_block,
               'block_form': AdminBlockForm(), 'current_page': _('AboutExperience'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/experience/admin.html', context)


@authenticated_staff
@staff_only
def AdminFrontPageAboutExperienceCreate(request):
    blocks = Block.objects.filter(type='AboutExperience')
    if request.method == 'POST':
        block_form = AdminBlockForm(request.POST, request.FILES)
        if block_form:
            title = request.POST.get('title')
            keywords = request.POST.get('keywords')
            keywords2 = request.POST.get('keywords2')
            category = request.POST.get('category')

            page = request.POST.get('page')
            order = request.POST.get('order')
            section = request.POST.get('section')
            description = request.POST.get('description')
            pdf = request.FILES.get('pdf')

            ######### education  block item ##########
            experience_title = request.POST.getlist('[experience_title]')
            experience_percentages = request.POST.getlist('[experience_percentages]')

            if category == '' or category == None:
                category = None
            else:
                category = FrontCategories.objects.get(id=category)

            if page == '' or page == None:
                page = None
            else:
                page = Pages.objects.get(id=page)

            try:
                block_object = Block.objects.get(type='AboutExperience')
                block_object.title = title
                block_object.keywords = keywords
                block_object.keywords2 = keywords2
                block_object.category = category
                block_object.page = page
                block_object.pdf = pdf
                block_object.section = section
                block_object.description = description
                block_object.save()


            except:
                block_object = Block(title=title, keywords=keywords, keywords2=keywords2, category=category, page=page,
                                     pdf=pdf, section=section, description=description, type='AboutExperience', order=0)
                block_object.save()

            ######### education  block item ##########
            for i in range(len(experience_title)):
                block_item = BlockItem(block=block_object, type='Experience', title=experience_title[i],
                                       percentage=experience_percentages[i], order=0)
                block_item.save()

            messages.success(request, _('About Experience Created Successfully'), extra_tags='AboutPage')
            return HttpResponseRedirect(reverse_lazy('front:AdminFrontPageAboutExperienceList'))
        else:
            messages.error(request, _('About Experience Not Created'), extra_tags='AboutPage')

    else:
        block_form = AdminBlockForm()

    context = {'blocks': blocks, 'block_form': AdminBlockForm(), 'current_page': _('AboutExperience'),

               }

    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/experience/add.html', context)


@authenticated_staff
@staff_only
def AdminFrontPageAboutExperienceUpdate(request,slug):
    blocks = Block.objects.get(slug=slug)
    block_items = BlockItem.objects.filter(block=blocks,type='Experience')
    for item in block_items:
        if item.percentage == 0:
            item.delete()

    if request.method == "POST":
        block_form = AdminBlockForm(request.POST or None, request.FILES or None)

        if block_form:
            title = request.POST.get('title')
            keywords = request.POST.get('keywords')
            keywords2 = request.POST.get('keywords2')
            category = request.POST.get('category')

            page = request.POST.get('page')
            order = request.POST.get('order')
            section = request.POST.get('section')
            description = request.POST.get('description')
            pdf = request.FILES.get('pdf')

            ######### education  block item ##########
            experience_slug = request.POST.getlist('[experience_slug]')
            experience_title = request.POST.getlist('[experience_title]')
            experience_percentages = request.POST.getlist('[experience_percentages]')

            print(experience_title)
            print(experience_percentages)
            print(experience_slug)

            if category == '' or category == None:
                category = None
            else:
                category = FrontCategories.objects.get(id=category)

            block_object = Block.objects.get(slug=slug)
            block_object.title = title
            block_object.keywords = keywords
            block_object.keywords2 = keywords2
            block_object.category = category
            block_object.page = page
            block_object.pdf = pdf
            block_object.section = section
            block_object.description = description
            block_object.save()

            ######### education  block item ##########
            i = 0
            for percentage in experience_percentages:
                 try:
                    if int(percentage) >= 0:
                        print('block item ', percentage)
                        object_slug = experience_slug[i]
                        block_item_object = BlockItem.objects.get(slug=object_slug)
                        block_item_object.title =experience_title[i]
                        block_item_object.percentage = percentage
                        block_item_object.save()
                    # if int(percentage) == 0:
                    #     object_slug = experience_slug[i]
                    #     block_item_object = BlockItem.objects.get(slug=object_slug)
                    #     block_item_object.delete()
                 except Exception as e:
                     print('block item 1 e ', e)


                 i +=1

            i = 0
            for percentage in experience_percentages:

                    try:
                        object_slug = experience_slug[i]
                        print('block item2 ', object_slug)
                        block_item_object = BlockItem.objects.get(slug=object_slug)

                    except Exception as e:
                        print('block item 2  e ', e)
                        if int(percentage) >= 0 and experience_title[i] != '' and experience_title[i] != None:
                            print('block item2 ', percentage)

                            block_item_object = BlockItem(block=block_object, title=experience_title[i],
                                                          percentage=percentage, type='Experience')
                            block_item_object.save()
                    i += 1


            messages.success(request, _("About Experience Add Successfully"), extra_tags='AboutPage')

            # return HttpResponseRedirect(reverse_lazy('front:AdminFrontPageAboutExperienceList'))
            return  redirect(request.META['HTTP_REFERER'])
        else:

            messages.error(request, _("About Experience Not Add , Please Try Again"), extra_tags='AboutPage')


    context = {'blocks': blocks,  'block_items':block_items,
               'block_form': AdminBlockForm(),

        'current_page': _('Update'), 'prev_Page': _('AboutExperience'),
        'prev_Page_link': reverse_lazy('front:AdminFrontPageAboutExperienceList'),

                }
    return render(request, f'{BACKEND_TEMPLATES}/front/blocks/about/experience/update.html', context)


@authenticated_staff
@staff_only
def AdminFrontPageAboutExperienceDelete(request, slug):
    block = Block.objects.get(slug=slug)
    block_item = BlockItem.objects.filter(block=block)
    for item in block_item:
        item.delete()

    block.delete()

    messages.success(request, _("About Experience Delete Successfully"), extra_tags='AboutPage')

    return HttpResponseRedirect(reverse_lazy('front:AdminFrontPageAboutExperienceList'))

