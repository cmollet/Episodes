import json
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from tvshow.utils.tvdb_api_wrap import TvdbApiClient

client = TvdbApiClient()

class Show(models.Model):
    tvdb_id = models.CharField(max_length=50)
    series_name = models.CharField(max_length=50)
    overview = models.TextField()
    banner = models.CharField(max_length=150, null=True, blank=True)
    imdb_id = models.CharField(max_length=50, null=True, blank=True)
    status_watched = models.BooleanField(default=False)
    slug = models.SlugField(null=True, blank=True)
    running_status = models.CharField(max_length=50)
    first_aired = models.DateField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True, auto_now_add=False)
    site_rating = models.DecimalField(max_digits=5, null=True, decimal_places=3, blank=True, default=0)
    user_rating = models.DecimalField(max_digits=5, null=True, decimal_places=3, blank=True, default=0)
    network = models.CharField(max_length=50)
    genre_list = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.series_name

    def add_show(self, data, runningStatus):
        self.series_name = data['seriesName']
        self.slug = slugify(self.series_name)
        self.overview = data['overview']
        self.banner = 'http://thetvdb.com/banners/' + data['banner']
        self.imbd_id = data['imdbID']
        self.tvdb_id = data['tvdbID']
        self.site_rating = data['siteRating']
        self.network = data['network']
        self.running_status = runningStatus
        self.genre_list = json.dumps(data['genre'])
        self.last_updated = timezone.now()
        try:
            self.first_aired = datetime.strptime(data['firstAired'], '%Y-%m-%d').date()
        except:
            pass
        self.save()

    @property
    def is_watched(self):
        flag = True
        season_count = Season.objects.filter(show=self)
        for season in season_count:
            if not season.status_watched_check and season.episode_count != 0:
                flag = False
                break
        return flag

    @property
    def episode_watch_count(self):
        return Episode.objects.filter(Q(season__show=self), Q(status_watched=True)).count()

    @property
    def total_episodes(self):
        return Episode.objects.filter(season__show=self).count()

    @property
    def get_genres(self):
        return json.loads(self.genre_list)

    @property
    def next_episode(self):
        return Episode.objects.filter(
            season__show=self,
            status_watched=False
        ).order_by(
            'first_aired',
            'number'
        ).first()

    def update_show_data(self):
        flag = False
        tvdbID = self.tvdb_id
        current_season = self.season_set.all().last()
        current_season_db_data = current_season.episode_set.all()
        current_season_oln_data = client.get_season_episode_list(tvdbID, current_season.number)
        counter = 0
        if current_season_oln_data:
            for db_episode, oln_episode in zip(current_season_db_data, current_season_oln_data):
                db_episode.compare_or_update(oln_episode)
                counter += 1
            if counter < len(current_season_oln_data):
                for new_episode in current_season_oln_data[counter:]:
                    if new_episode['episodeName'] == "":
                        new_episode['episodeName'] = 'TBA'
                    episode = Episode()
                    episode.add_episode(current_season, new_episode)
                    flag = True
        range_starter = current_season.number + 1
        new_seasons = client.get_all_episodes(tvdbID, range_starter)
        for i in range(len(new_seasons)):
            string = 'Season' + str(range_starter+i)
            season_data = new_seasons[string]
            season = Season()
            season.add_season(self, i+range_starter)
            season_episodes_data = new_seasons[string]
            flag = True
            for season_episode in season_episodes_data:
                if season_episode['episodeName']:
                    episode = Episode()
                    episode.add_episode(season, season_episode)
        return flag


class Season(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    number = models.IntegerField()
    status_watched = models.BooleanField(default=False)

    def __str__(self):
        showname = self.show.series_name
        return_string = showname + " S" + str(self.number)
        return return_string

    def add_season(self, show, number):
        self.show = show
        self.number = number
        self.save()

    def wst(self):
        self.show.save()
        if self.status_watched:
            self.episode_set.all().update(status_watched=False)
            self.status_watched = False
            self.save()
        else:
            self.episode_set.all().update(status_watched=True)
            self.status_watched = True
            self.save()

    @property
    def watch_count(self):
        return Episode.objects.filter(
            Q(season=self), Q(status_watched=True), Q(first_aired__lte=datetime.now())
        ).count()

    @property
    def episode_count(self):
        return Episode.objects.filter(Q(season=self), Q(first_aired__lte=datetime.now())).count()

    @property
    def status_watched_check(self):
        flag = self.watch_count == self.episode_count
        if self.status_watched is not flag:
            self.status_watched = flag
            self.save()
        return flag


class Episode(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    episode_name = models.CharField(max_length=255, blank=True, null=True)
    number = models.IntegerField()
    first_aired = models.DateField(null=True, blank=True)
    date_watched = models.DateField(null=True, blank=True, auto_now=True, auto_now_add=False)
    tvdb_id = models.CharField(max_length=50)
    overview = models.TextField(null=True, blank=True)
    status_watched = models.BooleanField(default=False)

    def __str__(self):
        showname = self.season.show.series_name
        return_string = showname + " S" + str(self.season.number) + "E" + str(self.number)
        return return_string

    def add_episode(self, season, data):
        self.season = season
        self.episode_name = data['episodeName']
        self.number = int(data['number'])
        try:
            self.first_aired = datetime.strptime(data['firstAired'], '%Y-%m-%d').date()
        except:
            pass
        self.tvdb_id = data['tvdbID']
        try:
            self.overview = data['overview']
        except:
            pass
        self.save()

    def wst(self):
        self.status_watched = not(self.status_watched)
        self.save()
        self.season.show.save()
        if self.season.watch_count == self.season.episode_count:
            self.season.status_watched = True
            self.season.save()
        else:
            self.season.status_watched = False
            self.season.save()

    def compare_or_update(self, new_data):
        self.episode_name = new_data['episodeName']
        self.save()
        if new_data['firstAired'] != "":
            try:
                self.first_aired = new_data['firstAired']
                self.save()
            except:
                pass
        if self.overview is None:
            self.overview = new_data['overview']
            self.save()
