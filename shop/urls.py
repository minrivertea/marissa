from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views


urlpatterns = patterns('',

    url(r'^$', views.index, name="home"),
    
    # wsfhome urls
    url(r'^wsfhome/$', views.wsf_home, name="wsf_home"),
    url(r'^wsfhome/products/$', views.wsf_categories, name="wsf_categories"),
    url(r'^wsfhome/products/(?P<cat>[\w-]+)/$', views.wsf_category, name="wsf_category"),
    url(r'^wsfhome/products/(?P<cat>[\w-]+)/(?P<sub_cat>[\w-]+)$', views.wsf_category, name="wsf_sub_category"),
    url(r'^wsfhome/product/(?P<slug>[\w-]+)/$', views.wsf_product_view, name="wsf_product_view"),
    
    # normal urls
    
    url(r'^get_quote/(?P<slug>[\w-]+)/$', views.get_quote, name="get_quote"),
    
    url(r'^account/$', views.account, name="account"),
    url(r'^account/(\w+)/$', views.account_order, name="account_order"),
    url(r'^contact-us/submit$', views.contact_us, name="contact_us"),
    url(r'^products/$', views.categories, name="categories"),
    url(r'^products/(?P<cat>[\w-]+)/$', views.category, name="category"),
    url(r'^products/(?P<cat>[\w-]+)/(?P<sub_cat>[\w-]+)$', views.category, name="sub_category"),
    url(r'^product/(?P<slug>[\w-]+)/review/$', views.review_product, name="review_product"),
    url(r'^product/(?P<slug>[\w-]+)/$', views.product_view, name="product_view"),
    url(r'^basket/$', views.basket, name="basket"),
    url(r'^basket/add/(\w+)$', views.add_to_basket, name="add_to_basket"),
    url(r'^basket/reduce/(\w+)$', views.reduce_quantity, name="reduce_quantity"),
    url(r'^basket/increase/(\w+)$', views.increase_quantity, name="increase_quantity"),
    url(r'^basket/remove/(\w+)$', views.remove_from_basket, name="remove_from_basket"),
    url(r'^order/step-one/$', views.order_step_one, name="order_step_one"),
    url(r'^order/confirm/$', views.order_confirm, name="order_confirm"),
    url(r'^order/complete/$', views.order_complete, name="order_complete"),
    url(r'^permission-denied/$', views.denied, name="denied"),
    url(r'^trade-shows/$', views.trade_shows, name="trade_shows"),
#    url(r'^order/complete/turn-off-twitter/(\w+)$', views.turn_off_twitter, name="turn_off_twitter"),    
    url(r'^reviews/$', views.reviews, name="reviews"),
    url(r'^review/thanks/$', direct_to_template, {'template': 'shop/review_thanks.html',}),
#    url(r'^tell-a-friend/$', views.tell_a_friend, name="tell_a_friend"),
    url(r'^not-me/$', views.not_you, name="not_you"),
)

