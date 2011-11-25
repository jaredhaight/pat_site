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

def view(request, jslug):
    photo = get_object_or_404(Photo, title_slug=str(jslug))
    caption = photo.caption

    try: prevphoto = photo.get_next_by_date_posted()
    except photo.DoesNotExist: prevphoto = None

    try: nextphoto = photo.get_previous_by_date_posted()
    except photo.DoesNotExist: nextphoto = None

    seed = Photo.objects.filter(id__lte=(photo.id)).order_by('-date_posted')[:5]

    if Photo.objects.filter(id__gt=photo.id).count() < 2:
        count = (4 - Photo.objects.filter(id__gt=photo.id).count())
    elif Photo.objects.filter(id__lt=photo.id).count() <2:
        count = seed.count()-1 
    else:
        count = 2

    pstrip = Photo.objects.filter(id__gte=(seed[count].id))[:5]
    plist = list(pstrip)
    plist.reverse()

    d  = dict(photo=photo, nextphoto=nextphoto, prevphoto=prevphoto, plist=plist, caption=caption, user=request.user)

    return render_to_response("view.html", d)

def details(request, jslug):
    photo = get_object_or_404(Photo, title_slug=str(jslug))
    caption = photo.caption

    try: prevphoto = photo.get_next_by_date_posted()
    except photo.DoesNotExist: prevphoto = None

    try: nextphoto = photo.get_previous_by_date_posted()
    except photo.DoesNotExist: nextphoto = None

    next = Photo.objects.filter(id__lt=(photo.id)).order_by('-date_posted')[:4]
    prev = Photo.objects.filter(id__gt=(photo.id)).order_by('date_posted')[:4]

    if next.count() < 4:
        prevlist = prev[:(4 - next.count())]
    else:
        prevlist = prev[:2]

    if prev.count() < 4:
        nextlist = next[:(4 - prev.count())]
    else:
        nextlist = next[:2]

    plist = [i for i in chain(prevlist, nextlist)]

    d = dict(photo=photo, nextphoto=nextphoto, prevphoto=prevphoto, plist=plist, caption=caption)

    return render_to_response("details.html", d)

def full(request, jslug):
    photo = get_object_or_404(Photo, title_slug=str(jslug))
    d = dict(photo=photo)

    return render_to_response("full.html", d)

def about(request):
    return render_to_response("about.html")

