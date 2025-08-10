from django.urls import path


from apps.front.views import views, blocks

app_name = 'front'

urlpatterns = [

    ########## Site Setting Admin #########
    path('front/site/', views.AdminFrontSiteSettingList, name='AdminFrontSiteSettingList'),
    path('front/site/create/', views.AdminFrontSiteSettingCreate, name='AdminFrontSiteSettingCreate'),
    path('front/site/update/<slug:slug>/', views.AdminFrontSiteSettingUpdate, name='AdminFrontSiteSettingUpdate'),
    path('front/site/delete/<slug:slug>/', views.AdminFrontSiteSettingDelete, name='AdminFrontSiteSettingDelete'),



    #################### Front Template #############################
    path('front/template/list', views.AdminFrontTemplateList, name='AdminFrontTemplateList'),
    path('front/template/create', views.AdminFrontTemplateCreate, name='AdminFrontTemplateCreate'),
    path('front/template/detail/<slug:slug>/', views.AdminFrontTemplateDetail, name='AdminFrontTemplateDetail'),
    path('front/template/update/<slug:slug>/', views.AdminFrontTemplateUpdate, name='AdminFrontTemplateUpdate'),
    path('front/template/delete/<slug:slug>/', views.AdminFrontTemplateDelete, name='AdminFrontTemplateDelete'),


    #################### Front Category #############################
    path('front/category/list', views.AdminFrontCategoryList, name='AdminFrontCategoryList'),
    path('front/category/detail/<slug:slug>/', views.AdminFrontCategoryDetail, name='AdminFrontCategoryDetail'),
    path('front/category/update/<slug:slug>/', views.AdminFrontCategoryUpdate, name='AdminFrontCategoryUpdate'),
    path('front/category/delete/<slug:slug>/', views.AdminFrontCategoryDelete, name='AdminFrontCategoryDelete'),


    #################### Front Tags #############################
    path('front/tags/', views.AdminFrontTagsList, name='AdminFrontTagsList'),
    path('front/tags/detail/<slug:slug>/', views.AdminFrontTagsDetail, name='AdminFrontTagsDetail'),
    path('front/tags/update/<slug:slug>/', views.AdminFrontTagsUpdate, name='AdminFrontTagsUpdate'),
    path('front/tags/delete/<slug:slug>/', views.AdminFrontTagsDelete, name='AdminFrontTagsDelete'),





    #################### Front Pages #############################
    path('front/pages/list', views.AdminFrontPagesList, name='AdminFrontPagesList'),
    path('front/pages/create', views.AdminFrontPagesCreate, name='AdminFrontPagesCreate'),
    path('front/pages/detail/<slug:slug>/', views.AdminFrontPagesDetail, name='AdminFrontPagesDetail'),
    path('front/pages/update/<slug:slug>/', views.AdminFrontPagesUpdate, name='AdminFrontPagesUpdate'),
    path('front/pages/delete/<slug:slug>/', views.AdminFrontPagesDelete, name='AdminFrontPagesDelete'),


    #################### Front Sections #############################
    path('front/sections/list', views.AdminFrontSectionsList, name='AdminFrontSectionsList'),
    path('front/sections/create', views.AdminFrontSectionsCreate, name='AdminFrontSectionsCreate'),
    path('front/sections/detail/<slug:slug>/', views.AdminFrontSectionsDetail, name='AdminFrontSectionsDetail'),
    path('front/sections/update/<slug:slug>/', views.AdminFrontSectionsUpdate, name='AdminFrontSectionsUpdate'),


    #################### Front Menu #############################
    path('front/menu/list', views.AdminFrontMenuList, name='AdminFrontMenuList'),
    path('front/menu/create', views.AdminFrontMenuCreate, name='AdminFrontMenuCreate'),
    path('front/menu/detail/<slug:slug>/', views.AdminFrontMenuDetail, name='AdminFrontMenuDetail'),
    path('front/menu/update/<slug:slug>/', views.AdminFrontMenuUpdate, name='AdminFrontMenuUpdate'),


    # #################### Front Menu Items #############################
    # path('front/menu/items/list', views.AdminFrontMenuItemsList, name='AdminFrontMenuItemsList'),
    # path('front/menu/items/create', views.AdminFrontMenuItemsCreate, name='AdminFrontMenuItemsCreate'),
    # path('front/menu/items/detail/<slug:slug>/', views.AdminFrontMenuItemsDetail, name='AdminFrontMenuItemsDetail'),
    # path('front/menu/items/update/<slug:slug>/', views.AdminFrontMenuItemsUpdate, name='AdminFrontMenuItemsUpdate'),
    # path('front/menu/items/delete/<slug:slug>/', views.AdminFrontMenuItemsDelete, name='AdminFrontMenuItemsDelete'),


    #################### Front Slider #############################
    # path('front/slider/list', views.AdminFrontSliderList, name='AdminFrontSliderList'),
    # path('front/slider/create', views.AdminFrontSliderCreate, name='AdminFrontSliderCreate'),
    # path('front/slider/detail/<slug:slug>/', views.AdminFrontSliderDetail, name='AdminFrontSliderDetail'),
    # path('front/slider/update/<slug:slug>/', views.AdminFrontSliderUpdate, name='AdminFrontSliderUpdate'),
    # path('front/slider/delete/<slug:slug>/', views.AdminFrontSliderDelete, name='AdminFrontSliderDelete'),


    # #################### Front Slider Item #############################
    # path('front/slider/item/list', views.AdminFrontSliderItemList, name='AdminFrontSliderItemList'),
    # path('front/slider/item/create', views.AdminFrontSliderItemCreate, name='AdminFrontSliderItemCreate'),
    # path('front/slider/item/detail/<slug:slug>/', views.AdminFrontSliderItemDetail, name='AdminFrontSliderItemDetail'),
    # path('front/slider/item/update/<slug:slug>/', views.AdminFrontSliderItemUpdate, name='AdminFrontSliderItemUpdate'),
    # path('front/slider/item/delete/<slug:slug>/', views.AdminFrontSliderItemDelete, name='AdminFrontSliderItemDelete'),


    #################### Front Banner  #############################
    path('front/banner/list', views.AdminFrontBannerList, name='AdminFrontBannerList'),
    path('front/banner/create', views.AdminFrontBannerCreate, name='AdminFrontBannerCreate'),
    path('front/banner/detail/<slug:slug>/', views.AdminFrontBannerDetail, name='AdminFrontBannerDetail'),
    path('front/banner/update/<slug:slug>/', views.AdminFrontBannerUpdate, name='AdminFrontBannerUpdate'),
    path('front/banner/delete/<slug:slug>/', views.AdminFrontBannerDelete, name='AdminFrontBannerDelete'),


    # #################### Front Banner Item #############################
    # path('front/banner/item/list', views.AdminFrontBannerItemList, name='AdminFrontBannerItemList'),
    # path('front/banner/item/create', views.AdminFrontBannerItemCreate, name='AdminFrontBannerItemCreate'),
    # path('front/banner/item/detail/<slug:slug>/', views.AdminFrontBannerItemDetail, name='AdminFrontBannerItemDetail'),
    # path('front/banner/item/update/<slug:slug>/', views.AdminFrontBannerItemUpdate, name='AdminFrontBannerItemUpdate'),
    # path('front/banner/item/delete/<slug:slug>/', views.AdminFrontBannerItemDelete, name='AdminFrontBannerItemDelete'),

#################### Front Testimonial  #############################
    path('front/testimonial/list', blocks.AdminFrontTestimonialList, name='AdminFrontTestimonialList'),
    path('front/testimonial/create', blocks.AdminFrontTestimonialCreate, name='AdminFrontTestimonialCreate'),
    path('front/testimonial/update/<slug:slug>/', blocks.AdminFrontTestimonialUpdate,
         name='AdminFrontTestimonialUpdate'),
    path('front/testimonial/delete/<slug:slug>/', blocks.AdminFrontTestimonialDelete,
         name='AdminFrontTestimonialDelete'),
    path('front/testimonial/delete/item/fromupdate/<slug:slug>/', blocks.AdminFrontTestimonialDeleteItemFromUpdate,
            name='AdminFrontTestimonialDeleteItemFromUpdate'),

    #################### Front Client Block #############################

    path('front/block/client/list', blocks.AdminFrontOurClientList, name='AdminFrontOurClientList'),
    path('front/block/client/create', blocks.AdminFrontOurClientCreate, name='AdminFrontOurClientCreate'),
    # path('front/block/client/detail/<slug:slug>/', blocks.AdminFrontOurClientDetail, name='AdminFrontOurClientDetail'),
    path('front/block/client/update/<slug:slug>/', blocks.AdminFrontOurClientUpdate, name='AdminFrontOurClientUpdate'),
    path('front/block/client/delete/<slug:slug>/', blocks.AdminFrontOurClientDelete, name='AdminFrontOurClientDelete'),

#################### Front Team Block #############################

    path('front/block/team/list', blocks.AdminFrontOurTeamList, name='AdminFrontOurTeamList'),
    path('front/block/team/create', blocks.AdminFrontOurTeamCreate, name='AdminFrontOurTeamCreate'),
    # path('front/block/client/detail/<slug:slug>/', blocks.AdminFrontOurClientDetail, name='AdminFrontOurClientDetail'),
    path('front/block/team/update/<slug:slug>/', blocks.AdminFrontOurTeamUpdate, name='AdminFrontOurTeamUpdate'),
    path('front/block/team/delete/<slug:slug>/', blocks.AdminFrontOurTeamDelete, name='AdminFrontOurTeamDelete'),







    #################### Front Block #############################
    path('front/block/list', views.AdminFrontBlockList, name='AdminFrontBlockList'),
    path('front/block/create', views.AdminFrontBlockCreate, name='AdminFrontBlockCreate'),
    path('front/block/detail/<slug:slug>/', views.AdminFrontBlockDetail, name='AdminFrontBlockDetail'),
    path('front/block/update/<slug:slug>/', views.AdminFrontBlockUpdate, name='AdminFrontBlockUpdate'),
    path('front/block/delete/<slug:slug>/', views.AdminFrontBlockDelete, name='AdminFrontBlockDelete'),
    path('front/block/delete/block/fromupdate/<slug:slug>/', views.AdminFrontBlockDeleteFromUpdate,
         name='AdminFrontBlockDeleteFromUpdate'),
    path('front/block/delete/item/fromupdate/<slug:slug>/', views.AdminFrontBlockDeleteItemFromUpdate,
         name='AdminFrontBlockDeleteItemFromUpdate'),
path('front/block/delete/item/all/fromupdate/<slug:slug>/', views.AdminFrontBlockDeleteItemAllFromUpdate,
         name='AdminFrontBlockDeleteItemAllFromUpdate'),


    ########  Home Page Blocks ########
    path('front/block/home/slider', blocks.AdminFrontBlockHomeSliderList, name='AdminFrontBlockHomeSliderList'),
    path('front/block/home/slider/create', blocks.AdminFrontBlockHomeSliderCreate, name='AdminFrontBlockHomeSliderCreate'),
    # path('front/block/home/slider/detail/<slug:slug>/', blocks.AdminFrontBlockHomeSliderDetail, name='AdminFrontBlockHomeSliderDetail'),
    path('front/block/home/slider/update/<slug:slug>/', blocks.AdminFrontBlockHomeSliderUpdate, name='AdminFrontBlockHomeSliderUpdate'),
    path('front/block/home/slider/delete/<slug:slug>/', blocks.AdminFrontBlockHomeSliderDelete, name='AdminFrontBlockHomeSliderDelete'),


    path('front/block/home/about/main/list', blocks.AdminFrontHomeAboutMainList, name='AdminFrontHomeAboutMainList'),
    path('front/block/home/about/main/create', blocks.AdminFrontHomeAboutMainCreate, name='AdminFrontHomeAboutMainCreate'),
    path('front/block/home/about/main/update/<slug:slug>/', blocks.AdminFrontHomeAboutMainUpdate, name='AdminFrontHomeAboutMainUpdate'),
    path('front/block/home/about/main/delete/<slug:slug>/', blocks.AdminFrontHomeAboutMainDelete, name='AdminFrontHomeAboutMainDelete'),

    path('front/block/home/swiper/list', blocks.AdminFrontHomeSwiperList, name='AdminFrontHomeSwiperList'),

    path('front/block/home/swiper/create', blocks.AdminFrontHomeSwiperCreate, name='AdminFrontHomeSwiperCreate'),
    path('front/block/home/swiper/update/<slug:slug>/', blocks.AdminFrontHomeSwiperUpdate, name='AdminFrontHomeSwiperUpdate'),
    path('front/block/home/swiper/delete/<slug:slug>/', blocks.AdminFrontHomeSwiperDelete, name='AdminFrontHomeSwiperDelete'),


    path('front/block/home/hero/main/list', blocks.AdminFrontHomeHeroMainList, name='AdminFrontHomeHeroMainList'),
    path('front/block/home/hero/main/create', blocks.AdminFrontHomeHeroMainCreate, name='AdminFrontHomeHeroMainCreate'),
    path('front/block/home/hero/main/update/<slug:slug>/', blocks.AdminFrontHomeHeroMainUpdate, name='AdminFrontHomeHeroMainUpdate'),
    path('front/block/home/hero/main/delete/<slug:slug>/', blocks.AdminFrontHomeHeroMainDelete, name='AdminFrontHomeHeroMainDelete'),
    path('front/block/home/hero/main/delete/videofromupdate/<slug:slug>/', blocks.AdminFrontHomeHeroMainDeleteVideoFromUpdate,
         name='AdminFrontHomeHeroMainDeleteVideoFromUpdate'),

    # #################### Front Block Item #############################
    path('front/block/portfolio/list', blocks.AdminFrontPortfolioList, name='AdminFrontPortfolioList'),
    path('front/block/portfolio/create', blocks.AdminFrontPortfolioCreate, name='AdminFrontPortfolioCreate'),
    path('front/block/portfolio/update/<slug:slug>/', blocks.AdminFrontPortfolioUpdate,
         name='AdminFrontPortfolioUpdate'),
    path('front/block/portfolio/delete/<slug:slug>/', blocks.AdminFrontPortfolioDelete,
         name='AdminFrontPortfolioDelete'),

    # #################### Front About Main Block Item #############################
#     path('front/block/about/main/list', blocks.AdminFrontAboutMainList, name='AdminFrontAboutMainList'),
#     path('front/block/about/main/create', blocks.AdminFrontAboutMainCreate, name='AdminFrontAboutMainCreate'),
    # path('front/block/item/detail/<slug:slug>/', views.AdminFrontBlockItemDetail, name='AdminFrontBlockItemDetail'),
    # path('front/block/item/update/<slug:slug>/', views.AdminFrontBlockItemUpdate, name='AdminFrontBlockItemUpdate'),
    # path('front/block/item/delete/<slug:slug>/', views.AdminFrontBlockItemDelete, name='AdminFrontBlockItemDelete'),


    #################### Front Hero Main Block Item #############################
    # path('front/block/hero/main/list', blocks.AdminFrontHeroMainList, name='AdminFrontHeroMainList'),
    # path('front/block/hero/main/create', blocks.AdminFrontHeroMainCreate, name='AdminFrontHeroMainCreate'),

 #################### Front Swiper Block #############################
    # path('front/block/swiper/list', blocks.AdminFrontSwiperList, name='AdminFrontSwiperList'),
    # path('front/block/swiper/create', blocks.AdminFrontSwiperCreate, name='AdminFrontSwiperCreate'),





    #################### About Page Block #############################
    path('front/block/page/about/hero', blocks.AdminFrontPageAboutHeroList, name='AdminFrontPageAboutHeroList'),
    path('front/block/page/about/hero/create', blocks.AdminFrontPageAboutHeroCreate, name='AdminFrontPageAboutHeroCreate'),
    path('front/block/page/about/hero/update/<slug:slug>/', blocks.AdminFrontPageAboutHeroUpdate, name='AdminFrontPageAboutHeroUpdate'),
    path('front/block/page/about/hero/delete/<slug:slug>/', blocks.AdminFrontPageAboutHeroDelete, name='AdminFrontPageAboutHeroDelete'),


    #################### About Page Block #############################
    path('front/block/page/about/cv', blocks.AdminFrontPageAboutCvList, name='AdminFrontPageAboutCvList'),
    path('front/block/page/about/cv/create', blocks.AdminFrontPageAboutCvCreate, name='AdminFrontPageAboutCvCreate'),
    path('front/block/page/about/cv/update/<slug:slug>/', blocks.AdminFrontPageAboutCvUpdate, name='AdminFrontPageAboutCvUpdate'),
    path('front/block/page/about/cv/delete/<slug:slug>/', blocks.AdminFrontPageAboutCvDelete, name='AdminFrontPageAboutCvDelete'),


    # #################### About Page Block Resume #############################
    path('front/block/page/about/resume', blocks.AdminFrontPageAboutResumeList, name='AdminFrontPageAboutResumeList'),
    path('front/block/page/about/resume/create', blocks.AdminFrontPageAboutResumeCreate, name='AdminFrontPageAboutResumeCreate'),
    path('front/block/page/about/resume/update/<slug:slug>/', blocks.AdminFrontPageAboutResumeUpdate, name='AdminFrontPageAboutResumeUpdate'),
    path('front/block/page/about/resume/delete/<slug:slug>/', blocks.AdminFrontPageAboutResumeDelete, name='AdminFrontPageAboutResumeDelete'),
    #
    #
    # #################### About Page Block Experience #############################
    path('front/block/page/about/experience', blocks.AdminFrontPageAboutExperienceList, name='AdminFrontPageAboutExperienceList'),
    path('front/block/page/about/experience/create', blocks.AdminFrontPageAboutExperienceCreate, name='AdminFrontPageAboutExperienceCreate'),
    path('front/block/page/about/experience/update/<slug:slug>/', blocks.AdminFrontPageAboutExperienceUpdate, name='AdminFrontPageAboutExperienceUpdate'),
    path('front/block/page/about/experience/delete/<slug:slug>/', blocks.AdminFrontPageAboutExperienceDelete, name='AdminFrontPageAboutExperienceDelete'),














]
