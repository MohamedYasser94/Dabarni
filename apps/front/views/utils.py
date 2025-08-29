from apps.front.models.models import *



User = get_user_model()


##########  Car Garage Admin #########

def FrontIndexFrontAppData(request):
    # template = Template.objects.all()
    # front_category = FrontCategories.objects.all()
    # tags = Tags.objects.all()
    # pages = Pages.objects.all()
    # sections = Sections.objects.all()
    # menus = Menu.objects.all()
    sliders = SliderItem.objects.filter(type = 'HomeSlider')
    try:
        home_about = Block.objects.filter(type='HomeAboutMain').last()
    except Exception as e:

        home_about = None
    home_about_item_one = BlockItem.objects.filter(block=home_about,creating_for='slider_order_one').last()
    home_about_item_two = BlockItem.objects.filter(block=home_about,creating_for='slider_order_two').last()
    home_about_item_three = BlockItem.objects.filter(block=home_about,creating_for='slider_order_three').last()
    portfolio = Block.objects.filter(type='Portfolio')

    try:
        home_service =  Block.objects.get(type='HomeSwiper')
    except Exception as e:

        home_service = None
    home_service_slider = BlockItem.objects.filter(block=home_service)
    try:
        work_section_block = Block.objects.get(type='PortfolioBlock')
    except Exception as e:

        work_section_block = None
    try:
        work_section_slider  = Block.objects.filter(type='Portfolio',show_on_home= 'Active')
    except Exception as e:
        work_section_slider = None


    # work_section_slider =Block.objects.filter(type='Portfolio',show_on_home= 'Active').last()

    try:
        hero_section = Block.objects.get(type='HomeHero')

    except Exception as e:

        hero_section = None

    try:
        hero_section_item = BlockItem.objects.filter(type='HomeHero').last()

    except Exception as e:

        hero_section_item = None


    banners = Banner.objects.all()
    banner_items = BannerItem.objects.all()
    try:
        testimonials = Testimonial.objects.filter(type='Testimonial').last()
    except Exception as e:

        testimonials = None
    testimonials_items = TestimonialItem.objects.all()
    blocks = Block.objects.all()
    blocks_items = BlockItem.objects.all()

    try:
        blogs_block = Block.objects.get(type='ArticleBlock')
    except Exception as e:

        blogs_block = None





    try:
        clients_section = Block.objects.get(type='Client')
    except Exception as e:

        clients_section = None
    clients_section_item = BlockItem.objects.filter(block=clients_section)

    context = {
        # 'template': template,
        # 'front_category': front_category,
        # 'tags': tags,
        # 'pages': pages,
        # 'sections': sections,
        # 'menus': menus,
        'portfolio': portfolio,
        'sliders': sliders,
        'banners': banners,
        'banner_items': banner_items,
        'testimonials': testimonials,
        'testimonials_items': testimonials_items,
        'blocks': blocks,
        'blocks_items': blocks_items,
        'clients_section': clients_section,
        'home_service': home_service,
        'home_service_slider': home_service_slider,
        'work_section_block': work_section_block,
        'work_section_slider': work_section_slider,
        'clients_section_item': clients_section_item,
        'home_about': home_about,
        'home_about_item_one': home_about_item_one,
        'home_about_item_two': home_about_item_two,
        'home_about_item_three': home_about_item_three,
        'hero_section': hero_section,
        'hero_section_item': hero_section_item,
        'blogs_block':blogs_block,

    }

    return context


def AdminGetCurrentUser(request):
    check_current_user = User.objects.get(id=request.user.id)



