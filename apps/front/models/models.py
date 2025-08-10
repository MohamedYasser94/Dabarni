from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string
from slugify import slugify

from helper.modelHelper import *
from helper.viewHelper import get_file_path

# Create your models here.


User = get_user_model()


class Template(models.Model):
    title = models.CharField(max_length=20, null=True, blank=True, )
    keyword = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    status = models.CharField(max_length=20, choices=Active_Status)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'template'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Template-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Template, self).save(*args, **kwargs)


class FrontCategories(models.Model):
    title = models.CharField(max_length=20, choices=Front_Category, default='Active', blank=True, null=True)
    keyword = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', blank=True, null=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'FrontCategories-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(FrontCategories, self).save(*args, **kwargs)


class Tags(models.Model):
    title = models.CharField(max_length=20, null=True, blank=True,)
    keyword = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    status = models.CharField(max_length=20, choices=Active_Status)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'category'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Tags-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Tags, self).save(*args, **kwargs)


class Pages(models.Model):
    title = models.CharField(max_length=20, choices=Page_Name, default='Other', blank=True, null=True, unique=True)
    keyword = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to=get_file_path)
    visibility = models.CharField(max_length=20, choices=Active_Status, blank=True, null=True, default='home')
    type = models.CharField(max_length=20, choices=Page_Type, default='Other', blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'page'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Pages-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Pages, self).save(*args, **kwargs)


class Sections(models.Model):
    page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='section_page', blank=True, null=True)
    title = models.CharField(max_length=20, null=True, blank=True,)
    keyword = models.CharField(max_length=100, blank=True, null=True)
    position = models.IntegerField(default=0)
    visibility = models.CharField(max_length=20, choices=Active_Status, blank=True, null=True, default='home')
    status = models.CharField(max_length=20, choices=Active_Status)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'section'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Sections-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Sections, self).save(*args, **kwargs)


class Menu(models.Model):
    title = models.CharField(max_length=20, null=True, blank=True,)
    keyword = models.CharField(max_length=100, blank=True, null=True)
    position = models.IntegerField(default=0)
    page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='menu_page', blank=True, null=True)
    visibility = models.CharField(max_length=20, choices=Active_Status, blank=True, null=True, default='home')
    status = models.CharField(max_length=20, choices=Active_Status)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    code = models.CharField(max_length=50, null=True, blank=True)
    url = models.URLField(blank=True, null=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    icon = models.CharField(max_length=50, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('position',)
        verbose_name = 'menu'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Menu-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Menu, self).save(*args, **kwargs)


class MenuItems(models.Model):
    title = models.CharField(max_length=20, null=True, blank=True,)
    keyword = models.CharField(max_length=100, blank=True, null=True)
    position = models.IntegerField(default=0)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='menu', blank=True, null=True)
    visibility = models.CharField(max_length=20, choices=Active_Status, blank=True, null=True, default='home')
    status = models.CharField(max_length=20, choices=Active_Status)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)
    code = models.CharField(max_length=50, null=True, blank=True)
    url = models.URLField(blank=True, null=True)
    page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='menu_item_page', blank=True, null=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    icon = models.CharField(max_length=50, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('position',)
        verbose_name = 'menu item'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'MenuItem-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)

        super(MenuItems, self).save(*args, **kwargs)


class Slider(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(FrontCategories, on_delete=models.CASCADE, related_name='slider_category', blank=True,
                                    null=True)
    page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='slider_page', blank=True, null=True)
    section = models.ForeignKey(Sections, on_delete=models.CASCADE, related_name='slider_section', blank=True,
                                null=True)
    description = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    image_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    details_page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='slider_details_page', blank=True,
                                     null=True)
    position_type = models.CharField(max_length=20, choices=Slider_Type, blank=True, null=True, default='Other')
    type = models.CharField(max_length=20, choices=Block_Type, default='Other', blank=True, null=True)
    order = models.IntegerField(default=0, null=True, blank=True,)
    status = models.CharField(max_length=20, choices=Active_Status)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'slider'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Slider-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Slider, self).save(*args, **kwargs)


class SliderItem(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True,)
    slider = models.ForeignKey(Slider, on_delete=models.CASCADE, related_name='slider', null=True, blank=True,)
    category = models.ForeignKey(FrontCategories, on_delete=models.CASCADE, related_name='slider_item_category',
                                 blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    image_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=Block_Type, default='Other', blank=True, null=True)
    details_page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='slider_item_details_page',
                                     blank=True, null=True)
    order = models.IntegerField(default=0, null=True, blank=True,)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, blank=True,default='Active')
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'slider item'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'SliderItem-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SliderItem, self).save(*args, **kwargs)


class Banner(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True,)
    category = models.ForeignKey(FrontCategories, on_delete=models.CASCADE, related_name='banner_category', blank=True,
                                 null=True)
    page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='banner_page', blank=True, null=True)
    section = models.ForeignKey(Sections, on_delete=models.CASCADE, related_name='banner_section', blank=True,
                                null=True)
    description = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    image_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    video = models.FileField(upload_to=get_file_path, blank=True, null=True)
    video_source = models.CharField(max_length=20, choices=VARIANTS, default='local', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    details_page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='banner_details_page', blank=True,
                                     null=True)

    order = models.IntegerField(default=0, null=True, blank=True,)
    status = models.CharField(max_length=20, choices=Active_Status,default='Active', null=True, blank=True,)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'banner'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Banner-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Banner, self).save(*args, **kwargs)


class BannerItem(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True,)
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE, related_name='banner', null=True, blank=True,)
    description = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    image_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    details_page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='banner_item_details_page',
                                     blank=True, null=True)
    order = models.IntegerField(default=0, null=True, blank=True,)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, blank=True,)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'banner item'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'BannerItem-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(BannerItem, self).save(*args, **kwargs)


class Testimonial(models.Model):
    title = models.CharField(max_length=100,blank=True, null=True)
    category = models.ForeignKey(FrontCategories, on_delete=models.CASCADE, related_name='testimonial_category',
                                    blank=True, null=True)
    page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='testimonial_page', blank=True, null=True)
    section = models.ForeignKey(Sections, on_delete=models.CASCADE, related_name='testimonial_section', blank=True,
                                null=True)
    description = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    gif = models.ImageField(upload_to=get_file_path, null=True, blank=True, )
    image_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    details_page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='testimonial_details_page',
                                     blank=True, null=True)
    type = models.CharField(max_length=20, choices=Block_Type, default='Other', blank=True, null=True)
    order = models.IntegerField(default=0,blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status,blank=True, null=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'testimonial'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Testimonial-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Testimonial, self).save(*args, **kwargs)


class TestimonialItem(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True,)
    title2 = models.CharField(max_length=100, null=True, blank=True, )
    testimonial = models.ForeignKey(Testimonial, on_delete=models.CASCADE, related_name='testimonial',blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    description2 = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    keywords2 = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    gif  = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    image_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    details_page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='testimonial_item_details_page',
                                     blank=True, null=True)

    order = models.IntegerField(default=0, null=True, blank=True,)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, blank=True,)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'testimonial item'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TestimonialItem-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(TestimonialItem, self).save(*args, **kwargs)


class Block(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True,)
    title2 = models.CharField(max_length=100, null=True, blank=True,)
    category = models.ForeignKey(FrontCategories, on_delete=models.CASCADE, related_name='block_category', blank=True,
                                 null=True)
    page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='block_page', blank=True, null=True)
    section = models.ForeignKey(Sections, on_delete=models.CASCADE, related_name='block_section', blank=True, null=True)
    page_style = models.CharField(max_length=20, choices=Page_Style, default='Style 1', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    keywords2 = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    image_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    file = models.FileField(null=True, blank=True, upload_to=get_file_path)
    video = models.FileField(null=True, blank=True, upload_to=get_file_path)
    video_id = models.CharField(max_length=50, null=True, blank=True)
    pdf = models.FileField(null=True, blank=True, upload_to=get_file_path)
    details_page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='block_details_page', blank=True,
                                     null=True)
    type = models.CharField(max_length=20, choices=Block_Type, default='Other', blank=True, null=True)
    creating_for = models.CharField(max_length=20, default='block', blank=True, null=True)

    duration = models.IntegerField(default=0, null=True, blank=True,)
    agency = models.CharField(max_length=20, default='block', blank=True, null=True)
    employee = models.CharField(max_length=20, default='block', blank=True, null=True)
    order = models.IntegerField(default=0, blank=True, null=True)
    number = models.IntegerField(default=0, blank=True, null=True)
    show_on_home = models.CharField(max_length=20, choices=Active_Status, default='Inactive', blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, null=True, blank=True,)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'block'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def get_image(self):
        try :
            image = self.image.url
        except Exception as e:
            image = None
        return image

    def get_portfolio_url(self):
        return reverse('home:FrontPortfolioDetails', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Block-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Block, self).save(*args, **kwargs)


class BlockItem(models.Model):
    title = models.CharField(max_length=100,null=True,blank=True)
    title2 = models.CharField(max_length=100, null=True, blank=True,)
    category = models.ForeignKey(FrontCategories, on_delete=models.CASCADE, related_name='block_item_category',
                                 blank=True, null=True)
    tag = models.ForeignKey(Tags, on_delete=models.CASCADE, related_name='block_item_tag', blank=True, null=True)
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='block', blank=True, null=True)
    page_style = models.CharField(max_length=20, choices=Page_Style, default='Other', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    description2 = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    keywords2 = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    image_url = models.URLField(blank=True, null=True)
    icon = models.CharField(max_length=50, null=True, blank=True)
    video_url = models.URLField(blank=True, null=True)
    video_id = models.CharField(max_length=50, null=True, blank=True)
    video_cover = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    details_page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='block_item_details_page',
                                     blank=True, null=True)
    type = models.CharField(max_length=20, choices=Block_Item_Type, default='Other', blank=True, null=True)
    skills = models.CharField(max_length=100, null=True, blank=True)
    demo = models.URLField(max_length=255, null=True, blank=True)
    files = models.FileField(null=True, blank=True, upload_to=get_file_path)
    video = models.FileField(null=True, blank=True, upload_to=get_file_path)

    pdf = models.FileField(null=True, blank=True, upload_to=get_file_path)
    cloud_file = models.URLField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=50, null=True, blank=True)
    featured = models.CharField(max_length=255, choices=Featured_Status, default='Inactive', null=True, blank=True)
    published_at = models.DateField(blank=True, null=True)
    number = models.CharField(max_length=50, null=True, blank=True)
    residence = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    percentage = models.IntegerField(default=0, blank=True, null=True)
    creating_for = models.CharField(max_length=20, default='block', blank=True, null=True)
    duration = models.IntegerField(default=0, null=True, blank=True,)
    agency = models.CharField(max_length=20, default='block', blank=True, null=True)
    employee = models.CharField(max_length=20, default='block', blank=True, null=True)
    order = models.IntegerField(default=0, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', blank=True, null=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'block item'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'BlockItem-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(BlockItem, self).save(*args, **kwargs)



class Faq(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True,)
    category = models.ForeignKey(FrontCategories, on_delete=models.CASCADE, related_name='faq_category', blank=True,
                                 null=True)
    page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='faq_page', blank=True, null=True)
    section = models.ForeignKey(Sections, on_delete=models.CASCADE, related_name='faq_section', blank=True,
                                null=True)
    question = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    image_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    details_page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='faq_details_page', blank=True,
                                     null=True)
    type = models.CharField(max_length=100, choices=Block_Type, default='Other', blank=True, null=True)
    order = models.IntegerField(default=0, null=True, blank=True,)
    status = models.CharField(max_length=100, choices=Active_Status, default='Active', blank=True, null=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=100, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'FAQ'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Faq-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Faq, self).save(*args, **kwargs)

class PrivacyPolicy(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True,)
    body = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    image_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    details_page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='privacy_policy_details_page', blank=True,
                                     null=True)
    type = models.CharField(max_length=100, choices=Block_Type, default='Other', blank=True, null=True)
    order = models.IntegerField(default=0, null=True, blank=True,)
    status = models.CharField(max_length=100, choices=Active_Status, default='Active', blank=True, null=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=100, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'Privacy Policy'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'PrivacyPolicy-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(PrivacyPolicy, self).save(*args, **kwargs)


class TermsAndConditions(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True,)
    body = models.TextField(blank=True, null=True)
    keywords = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=get_file_path, null=True, blank=True,)
    image_url = models.URLField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    details_page = models.ForeignKey(Pages, on_delete=models.CASCADE, related_name='terms_and_conditions_details_page', blank=True,
                                     null=True)
    type = models.CharField(max_length=100, choices=Block_Type, default='Other', blank=True, null=True)
    order = models.IntegerField(default=0, null=True, blank=True,)
    status = models.CharField(max_length=100, choices=Active_Status, default='Active', blank=True, null=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=100, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('title',)
        verbose_name = 'Terms and Conditions'  # verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse("category_list")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'TermsAndConditions-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(TermsAndConditions, self).save(*args, **kwargs)