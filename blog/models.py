from django.db import models
from marissa.slugify import smart_slugify

from tinymce import models as tinymce_models

class BlogEntry(models.Model):
    slug = models.SlugField(max_length=80)
    promo_image = models.ImageField(upload_to='images/blog-photos', blank=True, null=True)
    date_added = models.DateField()
    is_gallery = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=200)
    content = tinymce_models.HTMLField()
    
    def __unicode__(self):
        return self.slug
        
    def get_absolute_url(self):
        return "/blog/%s/" % self.slug # important! do not change (for feeds)
     
    def get_content(self):
        return self.summary
       
        
