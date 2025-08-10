
from core.models.blog import BlogArticle, CommonTags, BlogCategories,  BlogServices



def home_processors(request):
    try:
        return {'all_category': BlogCategories.objects.all(), 'all_tags': CommonTags.objects.all(),
                'all_work': BlogServices.objects.filter(service_type='Work'), 'all_services': BlogServices.objects.filter(service_type='Service'),
                'all_product': BlogServices.objects.filter(service_type='Product'), 'all_article': BlogArticle.objects.all(),
                'category_article': BlogCategories.objects.all(),

                }

    except Exception as e:
        return {'all_category': None, 'all_tags': None, 'all_work': None, 'all_services': None, 'all_product': None,

                'all_article': None, 'category_article': None, 'tag_article': None,



                }



def content_processors(request):


    try:
        return {
            'all_tags': CommonTags.objects.all(),
            'all_work': BlogServices.objects.all(),
            'all_services': BlogServices.objects.all(),
            'all_product': BlogServices.objects.all(),
            'all_article': BlogArticle.objects.all(),
            'category_article': BlogCategories.objects.all(),





                }



    except Exception as e:
        return {
            'all_tags': None,
            'all_work': None,
            'all_services': None,
            'all_product': None,
            'all_article': None,
            'category_article': None,

            'all_client': None,
            'all_testimonials': None,
                }





