# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from main.models import *


def home(request):
    """Home Page"""
    photos = get_list_or_404(Photo.objects.all().order_by("-date_posted"))
    paginator = Paginator(photos, 15)

    try: page = int(request.GET.get("page", '1'))
    except ValueError: page = 1

    try:
        photos = paginator.page(page)
    except (InvalidPage, EmptyPage):
        photos = paginator.page(paginator.num_pages)

    filmstrip = photos.object_list
 
    if "has_visited" in request.session:
        first_time = 'no'
    else:
        first_time = 'yes'
        request.session["has_visited"] = "Yes"

    return render_to_response("home.html", dict(photos=photos, filmstrip=filmstrip, user=request.user, first_time=first_time))

def category(request,jcat):
    photos = get_list_or_404(Photo.objects.filter(tags__name=jcat).order_by("-date_posted"))
    paginator = Paginator(photos, 15)

    try: page = int(request.GET.get("page", '1'))
    except ValueError: page = 1

    try:
        photos = paginator.page(page)
    except (InvalidPage, EmptyPage):
        photos = paginator.page(paginator.num_pages)

    filmstrip = photos.object_list

    return render_to_response("home.html", dict(photos=photos, flimstrip=filmstrip, user=request.user))

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
    filmstrip = list(pstrip)
    filmstrip.reverse()

    tagsobj  = photo.tags.all()
    tags = ''
    count = tagsobj.count()
    while count > 0:
        for tag in tagsobj:
            tags = tags + tag.name
            if count > 1:
                tags = tags + ', '
            count = count - 1

    d = dict(photo=photo, nextphoto=nextphoto, prevphoto=prevphoto, filmstrip=filmstrip, caption=caption, user=request.user, tags=tags)


    return render_to_response("view.html", d)

def about(request):
    return render_to_response("about.html")
