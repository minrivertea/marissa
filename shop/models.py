from django.db import models
from django.contrib.auth.models import User
from django.contrib.sitemaps import ping_google
from django.shortcuts import get_object_or_404
import logging
from datetime import datetime

from slugify import smart_slugify
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from django.template.loader import render_to_string
from django.core.mail import send_mail
from marissa import settings

from tinymce import models as tinymce_models



# these are the country choices for an address
UNITED_KINGDOM = 'united kingdom'
INVALID = 'invalid'
ALBANIA = 'albania'
ANDORRA = 'andorra'
ARMENIA = 'armenia'
AUSTRIA = 'austria'
BELARUS = 'be'
BELGIUM = 'belgium'
BOSNIA_HERZEGOVINA = 'bosnia and herzegovina'
BULGARIA = 'bulgaria'
CAPE_VERDE = 'cape verde'
CROATIA = 'croatia'
CYPRUS = 'cyprus'
CZECH_REPUBLIC = 'czech republic'
DENMARK = 'denmark'
ESTONIA = 'estonia'
FAROE_ISLANDS = 'faroe islands'
FINLAND = 'finland'
FRANCE = 'france'  
GEORGIA = 'georgia'
GERMANY = 'georgia' 
GIBRALTAR = 'gibraltar'
GREECE = 'greece' 
GREENLAND = 'greenland'
HUNGARY = 'hungary'
ICELAND = 'iceland'
IRELAND = 'ireland'  
ITALY = 'italy' 
LATVIA = 'latvia'
LIECHENSTEIN = 'liechenstein'
LITHUANIA = 'lithuania'
LUXEMBOURG = 'luxembourg'  
MACEDONIA = 'macedonia'
MALTA = 'malta'
MOLDOVA = 'moldova'
MONACO = 'monaco' 
NETHERLANDS = 'netherlands'
NORWAY = 'norway'
POLAND = 'poland'
PORTUGAL = 'portugal' 
ROMANIA = 'romania'
SAN_MARINO = 'san marino'
SLOVAK_REPUBLIC = 'slovak republic'
SLOVENIA = 'slovenia'
SPAIN = 'spain'
SWEDEN = 'sweden'
SWITZERLAND = 'switzerland'
TURKEY = 'turkey'
UKRAINE = 'ukraine'
COUNTRY_CHOICES = (
    (UNITED_KINGDOM, u"United Kingdom"),
    (INVALID, u"-----"),
    (ALBANIA, u"Albania"),
    (ANDORRA, u"Andorra"),
    (ARMENIA, u"Armenia"),
    (AUSTRIA, u"Austria"),
    (BELARUS, u"Belarus"),
    (BELGIUM, u"Belgium"),
    (BOSNIA_HERZEGOVINA, u"Bosnia and Herzegovina"),
    (BULGARIA, u"Bulgaria"),
    (CAPE_VERDE, u"Cape Verde"),
    (CROATIA, u"Croatia"),
    (CYPRUS, u"Cyprus"),
    (CZECH_REPUBLIC, u"Czech Republic"),
    (DENMARK, u"Denmark"),
    (ESTONIA, u"Estonia"),
    (FAROE_ISLANDS, u"Faroe Islands"),
    (FINLAND, u"Finland"),
    (FRANCE, u"France"),
    (GEORGIA, u"Georgia"),
    (GERMANY, u"Germany"), 
    (GIBRALTAR, u"Gibraltar"),
    (GREECE, u"Greece"), 
    (GREENLAND, u"Greenland"),
    (HUNGARY, u"Hungary"),
    (ICELAND, u"Iceland"),
    (IRELAND, u"Ireland"),  
    (ITALY, u"Italy"), 
    (LATVIA, u"Latvia"),
    (LIECHENSTEIN, u"Liechenstein"),
    (LITHUANIA, u"Lithuania"),
    (LUXEMBOURG, u"Luxembourg"),  
    (MACEDONIA, u"Macedonia"),
    (MALTA, u"Malta"),
    (MOLDOVA, u"Moldova"),
    (MONACO, u"Monaco"), 
    (NETHERLANDS, u"Netherlands"),
    (NORWAY, u"Norway"),
    (POLAND, u"Poland"),
    (PORTUGAL, u"Portugal"),
    (ROMANIA, u"Romania"),
    (SAN_MARINO, u"San Marino"),
    (SLOVAK_REPUBLIC, u"Slovak Republic"),
    (SLOVENIA, u"Slovenia"),
    (SPAIN, u"Spain"),
    (SWEDEN, u"Sweden"),
    (SWITZERLAND, u"Switzerland"),
    (TURKEY, u"Turkey"),
    (UKRAINE, u"Ukraine"),     
)


class ShopSettings(models.Model):
    ga_tracking_code = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='images/', blank=True, null=True,
        help_text="Should be exactly 400 x 100px")
    homepage_title = models.CharField(max_length=200, blank=True, null=True)
    homepage_description = tinymce_models.HTMLField()
    homepage_meta_description = models.CharField(max_length=200, blank=True, null=True)
    product_page_description = tinymce_models.HTMLField()
    contact_us_page = tinymce_models.HTMLField()
    show_prices = models.BooleanField(default=False)
    site_email = models.CharField(max_length=200, blank=True, null=True)


class Page(models.Model):
    slug = models.SlugField(max_length=80, 
        help_text="No special characters or spaces, just lowercase letters and '-' please!")
    title = models.CharField(max_length=255, 
        help_text="The title of the page")
    parent = models.ForeignKey('self', blank=True, null=True, 
        help_text="Link this page to a higher level page - must be one of the 1st level navigation items!!")
    content = tinymce_models.HTMLField()
    image = models.ImageField(upload_to="images/page-images", blank=True, null=True, 
        help_text="Optional - will appear on the page if you add it")
    template = models.CharField(max_length=255, blank=True, null=True, 
        help_text="Leave this field empty unless you know what you're doing.")
    
    def __unicode__(self):
        return self.title
    
    def get_children(self):
        pages = Page.objects.filter(parent=self)
        return pages


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80)
    description = tinymce_models.HTMLField()
    parent = models.ForeignKey("self", blank=True, null=True)
    image = models.ImageField(upload_to="images/category-photos")
    
    def __unicode__(self):
        return self.name
    
    def get_children(self):
        children = Category.objects.filter(parent=self)
        return children
    
    def products_count(self):
    	# find out how many products are in this category, and this category's children
    	count = 0
    	for product in Product.objects.filter(category=self):
    	    count +=1
    	
    	for category in self.get_children():
    	    for product in Product.objects.filter(category=category):
    	       count +=1
    	               
        return count
    
    

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80)
    meta_title = models.CharField(max_length=200, blank=True, null=True)		
    description = models.TextField()
    meta_description = models.TextField(blank=True, null=True)
    super_short_description = models.CharField(max_length=200)
    body_text = models.TextField()
    long_description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/product-photos')
    image_2 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_2_caption = models.CharField(max_length=200, blank=True)
    image_3 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_3_caption = models.CharField(max_length=200, blank=True)
    image_4 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_4_caption = models.CharField(max_length=200, blank=True)
    image_5 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_5_caption = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category)
    sku = models.CharField(max_length=200, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_private = models.BooleanField(default=False)
        
    def __unicode__(self):
        return self.name
      
    def get_absolute_url(self):
        return "%s/product/%s/" % (settings.PROJECT_URL, self.slug)  #important, do not change
    
    def get_lowest_price(self):
        prices = UniqueProduct.objects.filter(parent_product=self).order_by('price')[0]
        return prices
        
    
    def save(self, force_insert=False, force_update=False):
         super(Product, self).save(force_insert, force_update)
         try:
             ping_google()
         except Exception:
             # Bare 'except' because we could get a variety
             # of HTTP-related exceptions.
             pass 
 
class UniqueProduct(models.Model):
    weight = models.IntegerField(null=True, blank=True)
    weight_unit = models.CharField(help_text="Weight units", max_length=3, null=True, blank=True)
    price = models.DecimalField(help_text="Price", max_digits=8, decimal_places=2, null=True, blank=True)
    price_unit = models.CharField(help_text="Currency", max_length=3, null=True, blank=True)
    parent_product = models.ForeignKey(Product)
    description = models.TextField()
    available_stock = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return "%s (%s%s)" % (self.parent_product, self.weight, self.weight_unit)


class Shopper(models.Model):
    user = models.ForeignKey(User)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    subscribed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.email
        
    def get_addresses(self):
        addresses = Address.objects.filter(owner=self).order_by('-id')
        return addresses 
    
    def get_orders(self):
        orders = Order.objects.filter(owner=self).order_by('-date_paid')
        return orders
    
    def get_value(self):
        value = 0
        for order in self.get_orders():
            amount = order.get_amount()
            value += amount
        
        return value
            
class Review(models.Model):
    product = models.ForeignKey(Product)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    text = models.TextField()
    short_text = models.TextField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.product.name       
            
class Address(models.Model):
    owner = models.ForeignKey(Shopper)
    house_name_number = models.CharField(max_length=200)
    address_line_1 = models.CharField(max_length=200, blank=True, null=True)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    town_city = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    country = models.CharField(max_length=200, choices=COUNTRY_CHOICES, db_index=True)
    
    def __unicode__(self):
        return "%s, %s, %s" % (self.house_name_number, self.postcode, self.country)
    
       
        
class Basket(models.Model):
    date_modified = models.DateTimeField()
    owner = models.ForeignKey(Shopper, null=True) #can delete this
    
    def __unicode__(self):
        return str(self.date_modified)
 

class BasketItem(models.Model):  
    item = models.ForeignKey(UniqueProduct)
    quantity = models.PositiveIntegerField()
    basket = models.ForeignKey(Basket)
    
    def get_price(self):
        price = self.quantity * self.item.price
        return price
        
    def __unicode__(self):
        return "%s x %s" % (self.item, self.quantity)

    
class Discount(models.Model):
    discount_code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    discount_value = models.DecimalField(max_digits=3, decimal_places=2)
    is_active = models.BooleanField(default=False)
    
    
class Order(models.Model):
    items = models.ManyToManyField(BasketItem)
    is_confirmed_by_user = models.BooleanField(default=False)
    date_confirmed = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    is_free_sample = models.BooleanField(default=False)
    date_paid = models.DateTimeField(null=True)
    address = models.ForeignKey(Address, null=True)
    owner = models.ForeignKey(Shopper)
    discount = models.ForeignKey(Discount, null=True, blank=True)
    invoice_id = models.CharField(max_length=20)
    notes = models.TextField(null=True, blank=True)
    date_modified = models.DateTimeField(null=True)
    
    STATUS_RECEIVED = 'received'
    STATUS_INPRODUCTION = 'in production'
    STATUS_LOADED = 'loaded'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CHOICES = (
            (STATUS_RECEIVED, u"Received"),
            (STATUS_INPRODUCTION, u"In production"),
            (STATUS_LOADED, u"Loaded"),
            (STATUS_SHIPPED, u"Shipped"),
            (STATUS_DELIVERED, u"Delivered"),     
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    review_email_sent = models.BooleanField(default=False)
    
    
    def get_discount(self):
        total_price = 0
        for item in self.items:
            price = item.quantity * item.item.price
            total_price += price
        discount_amount = total_price * self.discount.discount_value
        return discount_amount
    
    def __unicode__(self):
        return self.invoice_id
    
    def get_amount(self):
        amount = 0
        for item in self.items.all():
            amount += item.get_price()
        if amount > 50:
            pass
        else:
            amount += settings.SHIPPING_PRICE
        return amount
          
            

# signals to connect to receipt of PayPal IPNs

def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    order = get_object_or_404(Order, invoice_id=ipn_obj.invoice)
    if order.status == Order.STATUS_PAID:
        return
        
    order.status = Order.STATUS_PAID
    order.date_paid = ipn_obj.payment_date
    order.is_paid = True
    order.save()
    
    # create and send an email to the customer
    invoice_id = order.invoice_id
    first_name = order.owner.first_name
    recipient = order.owner.email
    body = render_to_string('shop/emails/order_confirm_customer.txt', {
    	        'first_name': first_name, 
    	        'invoice_id': invoice_id, 
    	        'order_items': order.items.all(), 
    	        'order_status': order.status})
    subject_line = "Order confirmed - Min River Tea Farm" 
    email_sender = settings.SITE_EMAIL
      
    send_mail(
                  subject_line, 
                  body, 
                  email_sender,
                  [recipient], 
                  fail_silently=False
     )
     
     # create and send an email to me
    invoice_id = order.invoice_id
    email = order.owner.email
    recipient = 'mail@minrivertea.com'
    body = render_to_string('shop/emails/order_confirm_admin.txt', {
    	        'email': email, 
    	        'invoice_id': invoice_id, 
    	        'order_items': order.items.all(), 
    	        'order_status': order.status})
    subject_line = "NEW ORDER - %s" % invoice_id      
    email_sender = settings.SITE_EMAIL
      
    send_mail(
                  subject_line, 
                  body, 
                  email_sender,
                  [recipient], 
                  fail_silently=False
     )  
payment_was_successful.connect(show_me_the_money)    

    
def payment_flagged(sender, **kwargs):
    ipn_obj = sender
    order = get_object_or_404(Order, invoice_id=ipn_obj.invoice)
    order.status = Order.STATUS_PAYMENT_FLAGGED
    order.save()

     # create and send an email to me
    invoice_id = order.invoice_id
    email = order.owner.email
    recipient = 'mail@minrivertea.com'
    body = render_to_string('shop/emails/order_confirm_admin.txt', {'email': email, 'invoice_id': invoice_id, 'order_items': order.items.all()})
    subject_line = "FLAGGED ORDER - %s" % invoice_id 
    email_sender = 'mail@minrivertea.com'
      
    send_mail(
                  subject_line, 
                  body, 
                  email_sender,
                  [recipient], 
                  fail_silently=False
     )   
payment_was_flagged.connect(payment_flagged)






