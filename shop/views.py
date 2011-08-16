from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.template import RequestContext
from paypal.standard.forms import PayPalPaymentsForm
from django.http import HttpResponseRedirect 
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.urlresolvers import reverse

from PIL import Image
from cStringIO import StringIO
import os, md5
import datetime
import uuid
# import twitter
import re

from marissa.shop.models import *
from marissa.shop.forms import *
from marissa.slugify import smart_slugify



class BasketItemDoesNotExist(Exception):
    pass
    
class BasketDoesNotExist(Exception):
    pass
    

#render shortcut
def render(request, template, context_dict=None, **kwargs):
    return render_to_response(
        template, context_dict or {}, context_instance=RequestContext(request),
                              **kwargs
    )


# the homepage view
def index(request):
    
    # load variables 
    featured = Product.objects.filter(is_active=True, is_featured=True)      
    featured_one = featured[0:2]
    featured_two = featured[3:4]
    featured_three = featured[5:6] 
    featured_four = featured[7:8]  
    prices = UniqueProduct.objects.filter(is_active=True)
    review = Review.objects.all()[:2]
    
    
    return render(request, "shop/home.html", locals())

def page(request, slug, sub_page=None):
    if sub_page:
        page = get_object_or_404(Page, slug=sub_page)
    else:
        page = get_object_or_404(Page, slug=slug)
    
    if page.template:
        return render(request, page.template, locals())
    else:
    
        return render(request, "shop/page.html", locals())
    
# the product listing page
def categories(request):
    all_categories = Category.objects.filter(parent=None)

    return render(request, "shop/categories.html", locals())


# view for a category of products
def category(request, cat=None, sub_cat=None):

    # get a master list of products
    products = []
    
    # filter out private products if the user is not logged in
    if request.user.is_authenticated():
        all_products = Product.objects.filter(is_active=True)
    else:
        all_products = Product.objects.filter(is_active=True, is_private=False)
    
    # find the category from the slug
    if sub_cat:
        category = get_object_or_404(Category, slug=sub_cat)
    else:
        category = get_object_or_404(Category, slug=cat)

    children = category.get_children()
    
    for p in all_products:
        if p.category == category:
            products.append(p)
        for c in children:
            if p.category == c:
                products.append(p)

    # add in the prices information, and then merge the lists    
    prices = UniqueProduct.objects.filter(is_active=True)
    products_and_prices = []
    for product in products:
        products_and_prices.append((product, prices.filter(parent_product=product)))
    
    return render(request, "shop/categories.html", locals())


# view for a single product
def product_view(request, slug):
    try:
        added = request.session['ADDED']
    except:
        added = None
        
    if added:
        thing = get_object_or_404(BasketItem, id=request.session['ADDED'])
        message = "1 x %s%s added to your basket!" % (thing.item.weight, thing.item.weight_unit)
        request.session['ADDED'] = None
    
    product = get_object_or_404(Product, slug=slug)
    
    if product.is_private and not request.user.is_authenticated():
        return HttpResponseRedirect('/permission-denied/')
            
            
    
    prices = UniqueProduct.objects.filter(parent_product=product, is_active=True).order_by('price')
    other_products = Product.objects.filter(is_active=True, category=product.category).exclude(id=product.id)
    reviews = Review.objects.filter(product=product.id, is_published=True)[:2]
    
    if request.method == 'POST':
        form = ContactMeForm(request.POST)
        if form.is_valid():
            details = form.cleaned_data['info']

            # create email
            body = render_to_string('shop/emails/contact_request.txt', {
            	 'details': details,
            	 'product': product,
            })

            recipient = settings.PROJECT_EMAIL
            sender = settings.PROJECT_EMAIL
            subject_line = "%s - request for contact through website" % settings.PROJECT_NAME
                
            send_mail(
                          subject_line, 
                          body, 
                          sender,
                          [recipient], 
                          fail_silently=False
            )            
            
            
            request.session['MESSAGE'] = "1"
            url = reverse('product_view', args=[product.slug])
            return HttpResponseRedirect(url)
    
    else:
        form = ContactMeForm()
        try:
            if request.session['MESSAGE'] == "1":
                request.session['MESSAGE'] = None
                message = "Thanks, we'll get back to you as soon as possible."
        except:
            pass
    return render(request, "shop/product_view.html", locals())
    
def contact_us(request):
    try:
        if request.session['MESSAGE'] == "1":
            message = True
            request.session['MESSAGE'] = ""
    except:
        pass 
        
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            print "form is valid"
            # get cleaned data from form submission
            message = form.cleaned_data['your_message']
            your_name = form.cleaned_data['your_name']
            your_email = form.cleaned_data['your_email']
            country = form.cleaned_data['country']
            
            # create email
            body = render_to_string('shop/emails/contact_template.txt', {
            	 'message': message,
            	 'your_email': your_email,
            	 'your_name': your_name,
            	 'country': country,
            })

            recipient = settings.SITE_EMAIL
            sender = settings.SITE_EMAIL
            subject_line = "%s - website contact form submission" % settings.PROJECT_NAME
                
            send_mail(
                          subject_line, 
                          body, 
                          sender,
                          [recipient], 
                          fail_silently=False
            )
            
            
            url = request.META.get('HTTP_REFERER','/')
            request.session['MESSAGE'] = "1"
            return HttpResponseRedirect(url) 
    else:
        form = ContactForm() 
    
    return render(request, "shop/forms/contact_form.html", locals())        
   
# function for adding stuff to your basket
def add_to_basket(request, productID):
    product = get_object_or_404(UniqueProduct, id=productID)
    if request.user.is_anonymous:
        try:
            #try to find out if they already have a session open
            basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        except:
            #if not, we'll create one.
            basket = Basket.objects.create(date_modified=datetime.now())
            basket.save()
            request.session['BASKET_ID'] = basket.id
     
    try:
        item = BasketItem.objects.get(
            basket=basket,
            item=product,
        )
    except:
        item = BasketItem.objects.create(item=product, quantity=1, basket=basket)
        item.save()
    else:
        item.quantity += 1
        item.save()
        
    url = request.META.get('HTTP_REFERER','/')
    request.session['ADDED'] = item.id
    return HttpResponseRedirect(url)


# function for removing stuff from your basket
def remove_from_basket(request, productID):
    product = get_object_or_404(UniqueProduct, id=productID)
    if request.user.is_anonymous:
        #try to find out if they alread have a session cookie open with a basket
        try:
            basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        # if not, we'll return an error because nobody can remove an item 
        # from a basket that doesn't exist
        except BasketDoesNotExist:
            pass
    
    item = BasketItem.objects.get(
        basket=basket,
        item=product,
    )
    item.delete()
    
    return HttpResponseRedirect('/basket/') # Redirect after POST
    
# function for reducing the quantity of an item in your basket    
def reduce_quantity(request, productID):
    product = get_object_or_404(UniqueProduct, id=productID)
    
    # GET THE USER'S BASKET
    if request.user.is_anonymous:
        try:
            basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        except BasketDoesNotExist:
            pass
    
    basket_item = BasketItem.objects.get(basket=basket, item=product)
    if basket_item.quantity > 1:
        basket_item.quantity -= 1
        basket_item.save()
    else:
        pass
    
    return HttpResponseRedirect('/basket/') # Redirect after POST


# function for increasing the quantity of an item in your basket
def increase_quantity(request, productID):
    product = get_object_or_404(UniqueProduct, id=productID)
    
    # GET THE USER'S BASKET
    if request.user.is_anonymous:
        try:
            basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        except BasketDoesNotExist:
            pass

    
    basket_item = BasketItem.objects.get(basket=basket, item=product)
    basket_item.quantity += 1
    basket_item.save()
    
    return HttpResponseRedirect('/basket/') # Redirect after POST


# the view for your basket
def basket(request):

    try:
        basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
    except:
        basket = None        
                
    basket_items = BasketItem.objects.filter(basket=basket)
    total_price = 0
    for item in basket_items:
        price = item.quantity * item.item.price
        total_price += price
    
    if total_price > 50:
        postage_discount = True
    else:
        total_price += 3
        
    discount_form = UpdateDiscountForm()
        
    return render(request, "shop/basket.html", locals())



# the view for order process step 1 - adding your details
def order_step_one(request):
    try:
        basket = Basket.objects.get(id=request.session['BASKET_ID'])
    except:
        problem = "You don't have any items in your basket, so you can't process an order!"
        return render(request, 'shop/order-problem.html', locals())   

    try:
        order = get_object_or_404(Order, invoice_id=request.session['ORDER_ID'])
        # load their data from cookie
        if not order == None:    
            email = order.owner.email
            house_name_number = order.address.house_name_number
            address_line_1 = order.address.address_line_1
            address_line_2 = order.address.address_line_2
            town_city = order.address.town_city
            postcode = order.address.postcode
            country = order.address.country
            first_name = order.owner.first_name
            last_name = order.owner.last_name
    except:
        pass
    
    if request.user.is_authenticated():
        shopper = get_object_or_404(Shopper, user=request.user.id)

    if request.method == 'POST': 
        form = OrderStepOneForm(request.POST)
        
        # if the form has no errors...
        if form.is_valid(): 
        
            # get or create a user object
            if request.user.is_authenticated():
                this_user = request.user
            else:
                try:
                    this_user = get_object_or_404(User, email=form.cleaned_data['email'])
                except:
                    username = form.cleaned_data['email']
                    random_password = uuid.uuid1().hex
                    creation_args = {
                        'username': form.cleaned_data['email'],
                        'email': form.cleaned_data['email'],
                        'password': random_password,
                    }
                     
                    this_user = User.objects.create(**creation_args)
                    this_user.first_name = form.cleaned_data['first_name']
                    this_user.last_name = form.cleaned_data['last_name']
                    this_user.save()
                
                        
            # create a 'shopper' object
            try:
                shopper = get_object_or_404(Shopper, user=this_user.id)
            except:
                full_name = "%s %s" % (form.cleaned_data['first_name'], form.cleaned_data['last_name'])
                slugger = smart_slugify(full_name, lower_case=True)
                shopper = Shopper.objects.create(
                    user = this_user,
                    email = form.cleaned_data['email'],
                    first_name = form.cleaned_data['first_name'],
                    last_name = form.cleaned_data['last_name'],
                    subscribed = form.cleaned_data['subscribed'],
                    slug = slugger,     
                )
            
            # create an address based on the info they provided         
            address = Address.objects.create(
                owner = shopper,
                house_name_number = form.cleaned_data['house_name_number'],
                address_line_1 = form.cleaned_data['address_line_1'],
                address_line_2 = form.cleaned_data['address_line_2'],
                town_city = form.cleaned_data['town_city'],
                postcode = form.cleaned_data['postcode'],
                country = form.cleaned_data['country'],
            )
            
            # create an order object
            basket_items = BasketItem.objects.filter(basket=basket)
            order = Order.objects.create(
                is_confirmed_by_user = True,
                date_confirmed = datetime.now(),
                address = address,
                owner = shopper,
                status = Order.STATUS_CREATED_NOT_PAID,
                invoice_id = "TEMP"
            )
            
            # add the items to the order
            for item in basket_items:
                order.items.add(item)
                order.save()

            # give the order a unique ID
            order.invoice_id = "TEA-00%s" % (order.id)
            order.save()

            request.session['ORDER_ID'] = order.invoice_id  
            
            # finally, we'll log the user in secretly (they don't even know it!)
            from django.contrib.auth import load_backend, login
            for backend in settings.AUTHENTICATION_BACKENDS:
                if this_user == load_backend(backend).get_user(this_user.pk):
                    this_user.backend = backend
            if hasattr(this_user, 'backend'):
                login(request, this_user)
                         
            return HttpResponseRedirect('/order/confirm') 
        
        # if the form has errors...
        else:
             # load their data if they already tried to submit the form and failed.
             email = request.POST['email']
             house_name_number = request.POST['house_name_number']
             address_line_1 = request.POST['address_line_1']
             address_line_2 = request.POST['address_line_2']
             town_city = request.POST['town_city']
             postcode = request.POST['postcode']
             country = request.POST['country']
             first_name = request.POST['first_name']
             last_name = request.POST['last_name']

    confirm_form = OrderStepOneForm() 

    return render(request, 'shop/forms/order_step_one.html', locals())
 
 
# the view for 'logging out' if you're logged in with the wrong account   
def not_you(request):

	# remember the user's basket, otherwise they 'logout' but lose their own basket.
    this_user = request.user
    basket = Basket.objects.get(id=request.session['BASKET_ID'])
    
    # log the user out
    from django.contrib.auth import load_backend, logout
    for backend in settings.AUTHENTICATION_BACKENDS:
        if this_user == load_backend(backend).get_user(this_user.pk):
            this_user.backend = backend
    if hasattr(this_user, 'backend'):
        logout(request)
        # re-add the basket cookie so they don't lose their items
        request.session['BASKET_ID'] = basket.id
    
    # now they can return to the usual Step 1 of the form    
    return HttpResponseRedirect('/order/step-one/')    
    
    
    
# the view for the order step 2 - confirming your order
def order_confirm(request):
    shopper = get_object_or_404(Shopper, user=request.user)
    basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
    order = Order.objects.get(invoice_id=request.session['ORDER_ID'])
    order_items = BasketItem.objects.filter(basket=basket)
    total_price = 0
    for item in order_items:
        price = item.quantity * item.item.price
        total_price += price
    
    if total_price > 50:
        postage_discount = True
    else: 
        total_price += 3
        
    if request.method == 'POST': 
        form = OrderCheckDetailsForm(request.POST)
        basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        basket.delete()
        new_basket = Basket.objects.create(owner=shopper, date_modified=datetime.now())
        request.session['BASKET_ID'] = new_basket.id
        
        return False
        
        
    else:
        form = PayPalPaymentsForm()

    return render(request, 'shop/forms/order_confirm.html', locals())
   
    
    
    
def order_complete(request):
    # the user should be logged in here, so we'll find their Shopper object
    # or redirect them to home if they're not logged in
    try:
        shopper = get_object_or_404(Shopper, user=request.user)
    except:
        shopper = None
    
    try:
        order = get_object_or_404(Order, invoice_id=request.session['ORDER_ID'])
    except:
        pass
        
    # this line should reset the basket cookie. basically, if 
    # the user ends up here, they need to have a new basket
    request.session['BASKET_ID'] = None
    
    if request.method == 'POST':
        form = SubmitTwitterForm(request.POST)
        
        if form.is_valid():
            twitter_username = form.cleaned_data['twitter_username']

            # save the shopper's twitter_username to their profile
            shopper.twitter_username = twitter_username
            shopper.save()
            
            if shopper.get_orders() is not None:
                # create a tweet
                tweet =  render_to_string('shop/emails/tweet.txt', {'twitter_username': twitter_username})
            
                # tweet a message to them to say thanks for ordering!
                twitter_post(tweet)            
            else:
                pass      
    
            return render(request, 'shop/order_complete.html', locals())
            
     
    else: 
        form = SubmitTwitterForm()

    return render(request, "shop/order_complete.html", locals())


# the user can choose to not have their stuff tweeted
def turn_off_twitter(request, id):
    try:
        shopper = get_object_or_404(Shopper, pk=id)
    except:
        pass
    
    shopper.twitter_username = None
    shopper.save()
    return HttpResponseRedirect('/order/complete/')

# handles the review/testimonial view
def review_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            words = form.cleaned_data['text'] 
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            review = Review.objects.create(
                text=words,
                product=product,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            
            body = "%s %s just posted a review of %s" % (first_name, last_name, product.name)              
            subject_line = "New Review Posted - %s" % product.name 
            email_sender = settings.SITE_EMAIL
            recipient = settings.SITE_EMAIL
      
            send_mail(
                subject_line, 
                body, 
                email_sender,
                [recipient], 
                fail_silently=False
            )

            
            return HttpResponseRedirect('/review/thanks')
        
    else:
        form = ReviewForm()
    return render(request, "shop/forms/review_form.html", locals())

def send_review_email(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # create and send an email to the user to say thanks.
    body = render_to_string('shop/emails/review_email.txt', {
        'shopper': order.owner, 
        'items': order.items.all(),
        }
    )
                 
    subject_line = "%s - how to brew your tea" % settings.SITE_NAME
    email_sender = settings.SITE_EMAIL
    recipient = order.owner.email
      
    send_mail(
        subject_line, 
        body, 
        email_sender,
        [recipient], 
        fail_silently=False
    )
    
    order.review_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')   
        

# view for the photo wall
def reviews(request):
    reviews = Review.objects.filter(is_published=True)[:6]
    photos = Photo.objects.filter(published=True).order_by('-id')[:10]
    
    return render(request, 'shop/reviews.html', locals())

 
 
# view for the tell_a_friend form      
def tell_a_friend(request):
        
    if request.method == 'POST':
        form = TellAFriendForm(request.POST)
        if form.is_valid():
            
            # get cleaned data from form submission
            sender = form.cleaned_data['sender']
            message = form.cleaned_data['message']
            recipient = form.cleaned_data['recipient']
            
            # create email
            if message:
                body = render_to_string('shop/emails/custom_tell_friend.txt', {'message': message})
            else:
                body = render_to_string('shop/emails/tell_friend.txt', {'sender': sender})
            
            subject_line = "%s wants you to know about %s" % (sender, settings.SITE_NAME)
                
            send_mail(
                          subject_line, 
                          body, 
                          sender,
                          [recipient], 
                          fail_silently=False
            )
            
            # create the referrer/referee objects
            try:
                referrer = get_object_or_404(Shopper, email=sender)
                referrer.number_referred += 1
                referrer.save()
            except:
                referrer = Shopper.objects.create(email=sender, number_referred=1)
                referrer.save()
            
            referee = Referee.objects.create(
                    email=recipient,
                    referred_by=referrer,
                    )
            referee.save()
                 
            
            
            message = "We've sent an email to %s letting them know about - thanks for your help!" % (referee.email, settings.SITE_NAME)
            # then send them back to the tell a friend page
            return render(request, "shop/forms/tell_a_friend.html", locals())

        else:
            if form.non_field_errors():
                non_field_errors = form.non_field_errors()
            else:
                errors = form.errors
             
    else:
        form = TellAFriendForm()
    return render(request, 'shop/forms/tell_a_friend.html', locals())

# view for my private admin pages
def admin_stuff(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    
    # get the stats
    products = Product.objects.all()
    total_baskets = Basket.objects.all()
    total_orders = Order.objects.all()
    total_shoppers = Shopper.objects.all()
    published_photos = Photo.objects.filter(published=True)
    unpublished_photos = Photo.objects.filter(published=False)
    orders = Order.objects.all().filter(is_giveaway=False).order_by('-date_confirmed')
    giveaways = Order.objects.all().filter(is_giveaway=True).order_by('-date_confirmed')
    
    # work out how many sales we've made
    total_sales = 0
    for order in orders:
        total_sales += order.get_amount() 
    
    # make the nice lists for paid/unpaid orders
    all_orders = []    
    for order in orders:
        if order.status == Order.STATUS_CREATED_NOT_PAID:
            pass
        else:
            all_orders.append((order, order.items.all())) 
    
    all_giveaways = []
    for order in giveaways:
        all_giveaways.append((order, order.items.all()))

    return render(request, "shop/admin_base.html", locals())

#specific shopper view in admin-stuff
def admin_shopper(request, id):
    shopper = get_object_or_404(Shopper, pk=id)
    return render(request, 'shop/admin_shopper.html', locals())

# specific order view in admin-stuff
def admin_order(request, id):
    order = get_object_or_404(Order, pk=id)
    return render(request, 'shop/admin_order.html', locals())

# function for changing order status from admin-stuff
def ship_it(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    
    order = get_object_or_404(Order, pk=id)
    order.status = Order.STATUS_SHIPPED
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')

# function for sending the 'send sample to friend' email
def send_sampler_email(request, id):
    order = get_object_or_404(Order, pk=id)
    shopper = order.owner
    if order.sampler_email_sent:
        return False

    sender = settings.SITE_EMAIL
    recipient = shopper.email
            
    # create email
    body = render_to_string('shop/emails/send_sample_to_friend_email.txt', {'shopper': shopper})
    subject_line = "Give a tea gift to a friend, courtesy of the Min River Tea Farm"
    send_mail(
                      subject_line, 
                      body, 
                      sender,
                      [recipient], 
                      fail_silently=False
    )
    
    order.sampler_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')
    
@login_required   
def account(request):
    shopper = request.user.get_profile()
    orders = Order.objects.filter(owner=shopper).order_by('-date_confirmed')
    latest_products = Product.objects.all().order_by('-id')
    return render(request, "shop/account.html", locals())   
    
@login_required    
def account_order(request, id):
    order = get_object_or_404(Order, pk=id)
    shopper = request.user.get_profile()
    if not order.owner == shopper:
        return HttpResponseRedirect('/permission-denied/')
        
    return render(request, "shop/account_order.html", locals())
    

def denied(request):
    return render(request, "shop/denied.html", locals())    
    