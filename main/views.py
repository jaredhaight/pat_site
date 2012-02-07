# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.forms import ModelForm
from django.http import Http404
from main.models import *
from django.contrib.auth.models import User

from itertools import chain
import logging

def home(request):
    """Home Page"""
    photos = get_list_or_404(Photo.objects.all().order_by("-date_posted"))
    paginator = Paginator(photos, 4)

    try: page = int(request.GET.get("page", '1'))
    except ValueError: page = 1

    try:
        photos = paginator.page(page)
    except (InvalidPage, EmptyPage):
        photos = paginator.page(paginator.num_pages)
 
    return render_to_response("home.html", dict(photos=photos, user=request.user))

def category(request,jcat):
    photos = get_list_or_404(Photo.objects.filter(tags__icontains=jcat).order_by("-date_posted"))
    paginator = Paginator(photos, 4)

    try: page = int(request.GET.get("page", '1'))
    except ValueError: page = 1

    try:
        photos = paginator.page(page)
    except (InvalidPage, EmptyPage):
        photos = paginator.page(paginator.num_pages)

    return render_to_response("home.html", dict(photos=photos, user=request.user))

def view(request, jslug):
    photo = get_object_or_404(Photo, title_slug=str(jslug))
    caption = photo.caption

    try: prevphoto = photo.get_next_by_date_posted()
    except photo.DoesNotExist: prevphoto = None

    try: nextphoto = photo.get_previous_by_date_posted()
    except photo.DoesNotExist: nextphoto = None

    seed = Photo.objects.filter(id__lte=(photo.id)).order_by('-date_posted')[:15]

    if Photo.objects.filter(id__gt=photo.id).count() < 7:
        count = (14 - Photo.objects.filter(id__gt=photo.id).count())
    elif Photo.objects.filter(id__lt=photo.id).count() < 7:
        count = seed.count()-1 
    else:
        count = 7

    pstrip = Photo.objects.filter(id__gte=(seed[count].id))[:15]
    plist = list(pstrip)
    plist.reverse()

    row1 = plist[0:5]
    row2 = plist[5:10]
    row3 = plist[10:15]

    d = dict(photo=photo, nextphoto=nextphoto, prevphoto=prevphoto, row1=row1, row2=row2, row3=row3, caption=caption, user=request.user)


    return render_to_response("view.html", d)

def details(request, jslug):
    photo = get_object_or_404(Photo, title_slug=str(jslug))
    caption = photo.caption

    try: prevphoto = photo.get_next_by_date_posted()
    except photo.DoesNotExist: prevphoto = None

    try: nextphoto = photo.get_previous_by_date_posted()
    except photo.DoesNotExist: nextphoto = None

    seed = Photo.objects.filter(id__lte=(photo.id)).order_by('-date_posted')[:15]

    if Photo.objects.filter(id__gt=photo.id).count() < 7:
        count = (14 - Photo.objects.filter(id__gt=photo.id).count())
    elif Photo.objects.filter(id__lt=photo.id).count() < 7:
        count = seed.count()-1
    else:
        count = 7

    pstrip = Photo.objects.filter(id__gte=(seed[count].id))[:15]
    plist = list(pstrip)
    plist.reverse()

    row1 = plist[0:5]
    row2 = plist[5:10]
    row3 = plist[10:15]

    d = dict(photo=photo, nextphoto=nextphoto, prevphoto=prevphoto, row1=row1, row2=row2, row3=row3, caption=caption, user=request.user)

    return render_to_response("details.html", d)

def full(request, jslug):
    photo = get_object_or_404(Photo, title_slug=str(jslug))
    d = dict(photo=photo)

    return render_to_response("full.html", d)

def about(request):
    return render_to_response("about.html")

def download(request, jslug):
    photo = get_object_or_404(Photo, title_slug=str(jslug))
    response = photo.original_image.url
    
    return response
