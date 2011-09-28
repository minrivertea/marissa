from django.contrib.syndication.feeds import Feed
from marissa.blog.models import BlogEntry

class LatestEntries(Feed):
    title = "WeSourceFactories.com Blog"
    link = "/"
    description = "News and insights about sourcing from China by WeSourceFactories.com"

    def items(self):
        return BlogEntry.objects.order_by('-date_added')[:5]





