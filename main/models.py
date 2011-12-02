from django.db import models 
from django.template.defaultfilters import slugify 
from django.conf import settings 
from PIL import Image, ImageOps 
from PIL.ExifTags import TAGS 
from decimal import Decimal 
import os 
from os.path import exists 
import glob

class PhotoSize(models.Model):
    SIZE_CHOICES =(
        ('display', 'Display'),
        ('thumb', 'Thumbnail'),
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=SIZE_CHOICES)
    height = models.IntegerField()
    width = models.IntegerField()	    
    def __unicode__(self):
        return self.name

class Photo(models.Model):
    name = models.CharField(max_length=100)
    date_posted = models.DateField(blank=True)
    original_image = models.ImageField(upload_to='photos')
    caption = models.TextField(null=True, blank=True)
    title_slug = models.SlugField(null=True, blank=True, unique=True)
    rootfilename = models.CharField(max_length=50, editable=False, blank=True)
    num_views = models.PositiveIntegerField(editable=False, default=0)
    exif_iso = models.CharField(max_length=10, editable=False, null=True, blank=True)
    exif_aperture = models.CharField(max_length=10, editable=False, null=True, blank=True)
    exif_shutter = models.CharField(max_length=10, editable=False, null=True, blank=True)
    exif_focal = models.CharField(max_length=10, editable=False, null=True, blank=True)
    exif_date_taken = models.CharField(max_length=50, editable=False, null=True, blank=True)
    orientation = models.CharField(max_length=20, editable=False, null=True, blank=True)
    tags = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Photo, self).__init__(*args, **kwargs)
        self.get_sizes()

    sizes = PhotoSize.objects.all()        

    def create_sizes(self):
	for size in self.sizes:
            fname = (settings.MEDIA_ROOT + size.type.lower() + '/' + self.rootfilename + '_' + size.name.lower() + '.jpg')
            t_img = Image.open(self.original_image.path)
 
            if size.width == 0:
                width = t_img.size[0] * size.height / t_img.size[1]
            else:
                width = size.width

            if size.height == 0:
                height = t_img.size[1] * size.width / t_img.size[0]
            else:
                height = size.height

            if size.type == 'thumb':
                t_fit = ImageOps.fit(t_img, (height,width), Image.ANTIALIAS, 0, (0.5,0.5))
                t_fit.save(fname,"JPEG")
            elif size.type == 'display':
                t_img.thumbnail((width,height), Image.ANTIALIAS)
                t_img.save(fname, 'JPEG', quality=90)
 
    def get_orientation(self):
        width = self.original_image.width
        height = self.original_image.height

        if width > height:
            return 'landscape'

        if width < height:
            return 'portrait'

    def save(self, *args, **kwargs):
        self.rootfilename = (self.original_image.name).strip('photos/.jpg')
        super(Photo, self).save(*args, **kwargs)
        self.exif_iso = self.exif().get('ISOSpeedRatings')
        fnfirst,fnsec = self.exif().get('FNumber')
        self.exif_aperture = Decimal(fnfirst)/Decimal(fnsec)
        self.exif_shutter = '%s/%s'% (self.exif().get('ExposureTime'))
        ash,bsh = self.exif().get('FocalLength')
        self.exif_focal = ash/bsh
        date,time = (self.exif().get('DateTimeOriginal')).split()
        self.exif_date_taken = date.replace(':','/')+' at '+ time
        self.orientation = self.get_orientation()
        if self.date_posted == None:
            self.date_posted = datetime.datetime.today()
        super(Photo, self).save(*args, **kwargs)
	self.create_sizes()

    def delete(self):
        self.clear_photos()
        super(Photo, self).delete()

    def get_sizes(self):
        for size in self.sizes:
            setattr(self, ('get_'+size.name.lower()+'_url'), ('/'+ size.type + '/'+ self.rootfilename +'_'+size.name.lower()+'.jpg'))

    def exif(self):
        ret = {}
        i = Image.open(settings.MEDIA_ROOT + self.original_image.name)
        info = i._getexif()
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value
        return ret    
    
    def clear_photos(self):
        for item in glob.glob(settings.MEDIA_ROOT+'thumb/'+self.rootfilename+'*.jpg'):
            os.unlink(item)
        for item in glob.glob(settings.MEDIA_ROOT+'display/'+self.rootfilename+'*.jpg'):
            os.unlink(item)

    def admin_thumbnail(self):
        return u'<img src="%s"/>'% (settings.MEDIA_URL+self.get_view_url)
    admin_thumbnail.short_description  = 'Thumbnail'
    admin_thumbnail.allow_tags = True
