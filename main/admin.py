from django.contrib import admin
from main.models import Photo
from main.models import PhotoSize
from main.models import Tag

class PhotoAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ('name', 'date_posted', 'admin_thumbnail')
    prepopulated_fields = {'title_slug':('name',)}

class PhotoSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'height', 'width')

class TagAdmin(admin.ModelAdmin):
    list_disaply = ('name')

admin.site.register(Photo, PhotoAdmin)
admin.site.register(PhotoSize, PhotoSizeAdmin)
admin.site.register(Tag, TagAdmin)
