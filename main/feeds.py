from django.contrib.syndication.views import Feed
from django.utils.html import linebreaks
from main.models import Photo
import datetime

class pat_feed(Feed):
    title = "Photos and Text"
    link = "http://photosandtext.com"
    description = "Words and pictures from Photos and Text"

    def items(self):
        return Photo.objects.order_by("-date_posted")[:5]

    def item_title(self,item):
        return item.name

    def item_pubdate(self, item):
	return datetime.datetime.combine(item.date_posted,datetime.time())

    def item_description(self, item):
        return '<img src='+item.get_home_url+'><p>'+linebreaks(item.caption)+'</p><p>You can view this photo (and download a higher resolution version of it) <a href="%s">here</a>.' % item.get_absolute_url()

