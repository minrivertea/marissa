from django.conf import settings
from marissa.shop.models import *
from marissa.blog.models import BlogEntry


def common(request):
    from marissa import settings
    context = {}
    if settings.PAYMENTS_ACTIVE:
        context['paypal_return_url'] = settings.PAYPAL_RETURN_URL
        context['paypal_notify_url'] = settings.PAYPAL_NOTIFY_URL
        context['paypal_business_name'] = settings.PAYPAL_BUSINESS_NAME
        context['paypal_receiver_email'] = settings.PAYPAL_RECEIVER_EMAIL
        context['paypal_submit_url'] = settings.PAYPAL_SUBMIT_URL
        context['payments_active'] = True
    try:
        if '/wsfhome/' in request.path:
            context['shopsettings'] = get_object_or_404(ShopSettings, pk=2)
            context['wsfcategories'] = Category.objects.filter(parent__slug='wsf-home')
        else:
            context['shopsettings'] = get_object_or_404(ShopSettings, pk=1)
    except:
        pass
    context['sitename'] = settings.PROJECT_NAME
    context['siteemail'] = settings.PROJECT_EMAIL
    context['ga_is_on'] = settings.GA_IS_ON
    context['pages'] = Page.objects.all()
    context['all_products_count'] = Product.objects.all().count()
    return context

def get_products(request):
    products = Product.objects.filter(is_active=True)
    return {'products': products}

def get_categories(request):
    categories = Category.objects.filter(is_active=True)
    return {'categories': categories}

def get_basket(request):
    try:
        basket = Basket.objects.get(id=request.session['BASKET_ID'])
        basket_items = BasketItem.objects.filter(basket=basket)
    except:
        basket_items = None
    return {'basket_items': basket_items}
    
    
def get_basket_quantity(request):
    try:
        basket = Basket.objects.get(id=request.session['BASKET_ID'])
        basket_items = BasketItem.objects.filter(basket=basket)
        basket_quantity = 0
        for item in basket_items:
            basket_quantity += item.quantity
    except:
        basket_quantity = "0"
    
    return {'basket_quantity': basket_quantity}
    
def get_shopper(request):
    # find out if the user is logged in
    if request.user.is_authenticated():
        # check if there is a corresponding shopper
        try:
            shopper = get_object_or_404(Shopper, user=request.user)
        # if not, log them out because something's clearly wrong
        except:
            user = request.user
            from django.contrib.auth import load_backend, logout
            for backend in settings.AUTHENTICATION_BACKENDS:
                if user == load_backend(backend).get_user(user.pk):
                    user.backend = backend
            if hasattr(user, 'backend'):
                logout(request)
            shopper = None
    else:
        shopper = None
    
    return {'shopper': shopper}
