from datetime import timedelta
from random import shuffle

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect

from .models import Show, Season, Episode
from .utils.recommender import get_recommendations
from .utils.tvdb_api_wrap import search_series_list, get_series_with_id, get_all_episodes


@login_required
def home(request, view_type):
    if view_type == 'all':
        show_data = Show.objects.all().order_by('-modified')
        flag = False
    else:
        show_data = Show.objects.all().order_by('-modified')
        data = [show for show in show_data if not show.is_watched]
        show_data = data
        flag = True
    return render(request, 'tvshow/home.html', {'show_data': show_data, 'flag': flag})


@csrf_protect
def update_show(request):
    if request.method == 'POST':
        show_id = request.POST.get('show_info')
        show = Show.objects.get(id=show_id)
        if show:
            show.update_show_data()
            show.last_updated = timezone.now()
            show.save()
            return HttpResponseRedirect('/show/%s' % show.slug)
    return HttpResponseRedirect('/')


@csrf_protect
def update_show_rating(request):
    if request.method == 'POST':
        show_id = request.POST.get('show_id')
        show = Show.objects.get(id=show_id)
        if show:
            new_rating = request.POST.get('new_rating')
            show.userRating = new_rating
            show.save()
            return HttpResponseRedirect('/show/%s' % show.slug)
    return HttpResponseRedirect('/')


@csrf_protect
def add(request):
    if request.method == 'POST':
        slug = ''
        tvdbID = request.POST.get('show_id')
        runningStatus = request.POST.get('runningStatus')
        try:
            show = Show.objects.get(tvdb_id=tvdbID)
            slug = show.slug
        except Show.DoesNotExist as e:
            show_data = get_series_with_id(int(tvdbID))
            if show_data is not None:
                show = Show()
                show.add_show(show_data, runningStatus)
                slug = show.slug
                seasons_data = get_all_episodes(int(tvdbID), 1)
                for i in range(len(seasons_data)):
                    string = 'Season' + str(i+1)
                    season_data = seasons_data[string]
                    season = Season()
                    season.add_season(show, i+1)
                    season_episodes_data = seasons_data[string]
                    for season_episode in season_episodes_data:
                        if season_episode['episodeName']:
                            episode = Episode()
                            episode.add_episode(season, season_episode)
        return HttpResponseRedirect('/show/%s' % slug)
    return HttpResponseRedirect('/all')


@csrf_protect
def add_search(request):
    context = {}
    context['Flag'] = False
    if request.method == 'POST':
        search_string = request.POST.get('search_string')
        show_datalist = search_series_list(search_string)
        if show_datalist is not None:
            context['Flag'] = True
            context['show_datalist'] = show_datalist
    return render(request, 'tvshow/add_search.html', {'context': context})


@csrf_protect
def single_show(request, show_slug):
    show = Show.objects.get(slug__iexact=show_slug)
    next_episode = show.next_episode
    return render(request, 'tvshow/single.html', {'show': show, 'next_episode': next_episode})


@csrf_protect
def episode_swt(request):
    if request.method == 'POST':
        episode_id = request.POST.get('episode_swt')
        episode = Episode.objects.get(id=episode_id)
        if episode:
            episode.wst()
            show = episode.season.show
            return HttpResponseRedirect('/show/%s' % show.slug)
    return HttpResponseRedirect('/all')


@csrf_protect
def season_swt(request):
    if request.method == 'POST':
        season_id = request.POST.get('season_swt')
        season = Season.objects.get(id=season_id)
        if season:
            season.wst()
            show = season.show
            return HttpResponseRedirect('/show/%s' % show.slug)
    return HttpResponseRedirect('/all')


def recommended(request):
    try:
        predictions = get_recommendations()
    except:
        predictions = []
    predicted_shows = []
    for prediction in predictions:
        predicted_shows.append(get_series_with_id(prediction))
    shuffle(predicted_shows)
    return render(request, 'tvshow/recommended.html', {'predicted_shows': predicted_shows})


def search(request):
    search_query = request.GET.get('query')
    show_list = Show.objects.filter(series_name__icontains=search_query)
    episode_list = Episode.objects.filter(
        Q(episode_name__icontains=search_query) | Q(overview__icontains=search_query)
    )[:10]
    if (show_list or episode_list) and search_query:
        return render(request, 'tvshow/search_page.html', {'show_data': show_list, 'episode_list': episode_list})
    return HttpResponseRedirect('/all')


def update_all_continuing(request):
    show_list = Show.objects.filter(
        Q(running_status='Continuing'), Q(last_updated__lte=timezone.now()-timedelta(days=7))
    )
    for show in show_list:
        flag = show.update_show_data()
        show.last_updated = timezone.now()
        show.save()
        if flag:
            messages.success(request, '%s has been updated.' % show.seriesName)
    return HttpResponseRedirect('/')


@csrf_protect
def delete_show(request):
    if request.method == 'POST':
        show_id = request.POST.get('show_id')
        if show_id:
            try:
                show = Show.objects.get(id=show_id)
                show.delete()
                return HttpResponseRedirect('/')
            except:
                return HttpResponseRedirect('/')
    return HttpResponseRedirect('/')
