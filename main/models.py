from django.db import models 
from django.template.defaultfilters import slugify 
from django.conf import settings 
from PIL import Image, ImageOps 
from PIL.ExifTags import TAGS 
from decimal import Decimal 
import os 
from os.path import exists 
import glob
import boto
import settings
import datetime

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

class Tag(models.Model):
    name = models.CharField(max_length=100)
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
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Photo, self).__init__(*args, **kwargs)
        self.get_sizes()

    sizes = PhotoSize.objects.all()        

    def create_sizes(self):
        for size in self.sizes:
            fname = (settings.MEDIA_ROOT + size.type.lower() + '/' + self.rootfilename + '_' + size.name.lower() + '.jpg')
            s3 = boto.connect_s3(settings.dl_aws_access_key_id, settings.dl_aws_secret_access_key)
            bucket = s3.get_bucket('files.photosandtext')
            keyname = (size.type.lower() + '/' + self.rootfilename + '_' + size.name.lower() + '.jpg')

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
                t_fit.save(fname,"JPEG", quality=90)

                if bucket.get_key(keyname):
                    bucket.delete_key(keyname)
                    
                key = bucket.new_key(keyname)
                key.set_contents_from_file(open(fname))
                key.set_acl('public-read')

            elif size.type == 'display':
                t_img.thumbnail((width,height), Image.ANTIALIAS)
                t_img.save(fname, 'JPEG', quality=90)

                if bucket.get_key(keyname):
                    bucket.delete_key(keyname)

                key = bucket.new_key(keyname)
                key.set_contents_from_file(open(fname))
                key.set_acl('public-read')
 
    def get_orientation(self):
        width = self.original_image.width
        height = self.original_image.height

        if width > height:
            return 'landscape'

        if width < height:
            return 'portrait'

    def save(self, *args, **kwargs):
        #Get the root file name, this will be used for thumbnails, ec2, etc.
        self.rootfilename = (self.original_image.name).strip('photos/.jpg')

        #Save the file we uploaded, for the rest of this we'll need a physical file to work with
        super(Photo, self).save(*args, **kwargs)

    #Dump exif info
        try:
            self.exif_iso = self.exif().get('ISOSpeedRatings')
        except:
            self.exif_iso = 'None'            
        try:
            fnfirst,fnsec = self.exif().get('FNumber')
            self.exif_aperture = Decimal(fnfirst)/Decimal(fnsec)
        except:
            self.exif_aperture = 'None'            
        try:   
            exif_a,exif_b = self.exif().get('ExposureTime')
            if exif_b == 1:
                self.exif_shutter = '%s seconds'% (exif_a)
            else:
                self.exif_shutter = '%s/%s'% (exif_a,exif_b)
        except:
            self.exif_shutter = 'None'
        try:
            ash,bsh = self.exif().get('FocalLength')
            self.exif_focal = ash/bsh
        except:
            self.exif_focal = 'None'
        try:    
            date,time = (self.exif().get('DateTimeOriginal')).split()
            self.exif_date_taken = date.replace(':','/')+' at '+ time
        except:
            self.exif_date_taken = 'None'

        self.orientation = self.get_orientation()
        
        if self.date_posted == None:
            self.date_posted = datetime.datetime.today()

        #Save everything to DB, create thumbnails and upload everything to S3
        super(Photo, self).save(*args, **kwargs)
        self.create_sizes()
        self.upload_to_s3()

    def delete(self):
        self.clear_photos()
        super(Photo, self).delete()

    def get_sizes(self):
        for size in self.sizes:
            setattr(self, ('get_'+size.name.lower()+'_url'), (settings.MEDIA_URL + size.type + '/'+ self.rootfilename +'_'+size.name.lower()+'.jpg'))

    def exif(self):
        ret = {}
        i = Image.open(settings.MEDIA_ROOT + self.original_image.name)
        info = i._getexif()
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value
        return ret    
    
    def clear_photos(self):
        s3 = boto.connect_s3(settings.dl_aws_access_key_id, settings.dl_aws_secret_access_key)
        bucket = s3.get_bucket('files.photosandtext')
        for size in self.sizes:
            bucket.delete_key(size.type.lower() + '/' + self.rootfilename + '_' + size.name.lower() + '.jpg')
        for item in glob.glob(settings.MEDIA_ROOT+'thumb/'+self.rootfilename+'*.jpg'):
            os.unlink(item)
        for item in glob.glob(settings.MEDIA_ROOT+'display/'+self.rootfilename+'*.jpg'):
            os.unlink(item)
        bucket.delete_key(self.original_image.name)
        

    def admin_thumbnail(self):
        return u'<img src="%s"/>'% (self.get_filmstrip_url)
    admin_thumbnail.short_description  = 'Thumbnail'
    admin_thumbnail.allow_tags = True

    def upload_to_s3(self):
        s3 = boto.connect_s3(settings.dl_aws_access_key_id, settings.dl_aws_secret_access_key)
        bucket = s3.get_bucket('dl.photosandtext')
        keyname = self.original_image.name

        if bucket.get_key(keyname):
            bucket.delete_key(keyname)
        
        key = bucket.new_key(keyname)
        key.set_metadata('Content-Type','application/octet-stream')
        key.set_metadata('Content-Disposition','attachment')
        key.set_metadata('X-PAT-NAME',self.name)
        key.set_contents_from_file(open(self.original_image.path))
        key.set_acl('public-read')

    def get_absolute_url(self):
        return 'http://photosandtext.com/photo/'+self.title_slug
