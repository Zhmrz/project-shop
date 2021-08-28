from django.shortcuts import render
from django.views.generic import DetailView, View
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from .models import Laptop, Smartphone, LatestProducts, Customer, Cart, CartProduct


class BaseView(View):

    def get(self, request, *args, **kwargs):
        products = LatestProducts.objects.get_products_for_main_page('laptop', 'smartphone')
        context = {
            'products': products
        }
        return render(request, 'index.html', context)


class ProductDetailView(DetailView):

    CT_MODEL_MODEL_CLASS={
        'laptop': Laptop,
        'smartphone': Smartphone
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset=self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)


    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        return context


class CartView(View):

    def get(self, request, *args, **kwargs):
        customer = Customer.objects.get(user=request.user)
        cart = Cart.objects.get(owner=customer)
        context = {
            'cart': cart
        }
        return render(request, 'cart.html', context)


# class AddToCartView(View):
#
#     def get(self, request, *args, **kwargs):
#
#         ct_model, slug = kwargs.get('ct_model'), kwargs.get('slug')
#         customer = Customer.objects.get(user=request.user)
#         cart = Cart.objects.get(owner=customer, in_order=False)
#         content_type = ContentType.objects.get(model=ct_model)
#         product=content_type.model_class().objects.create(slug=product_slug)
#         cart_product = CartProduct.objects.create(
#             user=cart.owner, cart=cart, content_object=
#         )
#         return HttpResponseRedirect('/cart/')

