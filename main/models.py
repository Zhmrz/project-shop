from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse

User = get_user_model()

def get_product_url(obj, viewname):
    ct_model=obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})

"""
1. Product (meta)
2. Category
3. Cart
4. CartProduct
5. Users
6. Order
"""

class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model=ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                    )
        return products


class LatestProducts:

    objects = LatestProductsManager()


class Category(models.Model):

    name = models.CharField(max_length=250, verbose_name='Название категории')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(max_length=250, verbose_name='Имя продукта')
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name="Изображение")
    description = models.TextField(verbose_name="Описание", null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.name


class CartProduct(models.Model):

    user = models.ForeignKey("Customer", verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    amount = models.PositiveIntegerField(verbose_name="Количество", default=1)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая стоимость')

    def __str__(self):
        return f"Продукт: {self.content_object.name} (для корзины)"


class Cart(models.Model):

    owner = models.ForeignKey("Customer", verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена', default=0)
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона')
    adress = models.CharField(max_length=250, verbose_name='Адрес')

    def __str__(self):
        return f'Покупатель: {self.user.first_name} {self.user.last_name}'


class Laptop(Product):

    diagonal = models.CharField(max_length=250, verbose_name='Диагональ')
    display_type = models.CharField(max_length=250, verbose_name="Тип матрицы")
    processor_freq = models.CharField(max_length=250, verbose_name='Частота процессора')
    ram = models.CharField(max_length=250, verbose_name="Оперативная память")
    video = models.CharField(max_length=250, verbose_name="Видеокарта")
    time_battery = models.CharField(max_length=250, verbose_name="Время работы аккумулятора")

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class Smartphone(Product):

    diagonal = models.CharField(max_length=250, verbose_name='Диагональ')
    display_type = models.CharField(max_length=250, verbose_name="Тип матрицы")
    resolution = models.CharField(max_length=250, verbose_name="Разрешение экрана")
    ram = models.CharField(max_length=250, verbose_name="Оперативная память")
    accum_volume = models.CharField(max_length=250, verbose_name="Объем батареи")
    sd = models.BooleanField(default=True, verbose_name="Наличие SD карты")
    sd_volume_max = models.CharField(
        max_length=250, null=True, blank=True, verbose_name='Максимальный объем встраиваемой памяти'
    )
    main_cam_mp = models.CharField(max_length=250, verbose_name="Главная камера")
    frontal_cam_mp = models.CharField(max_length=250, verbose_name="Фронтальная камера")

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')