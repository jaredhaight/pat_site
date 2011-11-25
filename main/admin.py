from django.contrib import admin
from main.models import Photo
from main.models import PhotoSize

class PhotoAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ('name', 'date_posted', 'admin_thumbnail')
    prepopulated_fields = {'title_slug':('name',)}

class PhotoSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'height', 'width')

admin.site.register(Photo, PhotoAdmin)
admin.site.register(PhotoSize, PhotoSizeAdmin)
