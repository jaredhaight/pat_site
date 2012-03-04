from django.contrib.syndication.views import Feed
from django.utils.html import linebreaks
from main.models import Photo

class pat_feed(Feed):
    title = "Photos and Text"
    link = "http://photosandtext.com"
    description = "Words and pictures from Photos and Text"

    def items(self):
        return Photo.objects.order_by("-date_posted")[:5]

    def item_title(self,item):
        return item.name

    def item_description(self, item):
        return '<img src='+item.get_home_url+'><p>'+linebreaks(item.caption)

