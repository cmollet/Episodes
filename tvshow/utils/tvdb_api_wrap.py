import logging
import os
import time

import requests
from django.conf import settings
from django.utils import timezone


logger = logging.getLogger(__name__)

# Time in seconds to wait in between requests to TVDB
REQUEST_INTERVAL = 0.25

# Time in seconds for a token to be considered valid
TOKEN_VALID_TIME = 86400  # 24 hours


def json_request(url, params=None, headers=None, resp_key='data'):
    try:
        req = requests.get(url, params=params, headers=headers)
    except requests.exceptions.ConnectionError as exc:
        msg = f'Network error attempting to connect to {url}:\n{exc}'
        logger.error(msg)
        return
    try:
        resp = req.json()
    except ValueError:
        msg = f'Invalid JSON response from {url}'
        logger.error(msg)
        return
    try:
        return resp[resp_key]
    except KeyError:
        msg = f'{resp_key} key not found in response from {url}. Actual keys are {resp.keys()}'
        logger.error(msg)
        return


def download_image(url, slug):
    try:
        req = requests.get(url, stream=True)
    except requests.exceptions.ConnectionError as exc:
        msg = f'Network error attempting to connect to {url}:\n{exc}'
        logger.error(msg)
        return
    if req.status_code >= 400:
        logger.error(f"Unable to download image at {url}.\nStatus code: {req.status_code}")
        return
    slug = slug + '.jpg'
    with open(os.path.join('media_cdn', os.path.basename(slug)), 'wb') as image_file:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                image_file.write(chunk)
    return os.path.join('media', os.path.basename(slug))


class TvdbApiClient:
    def __init__(
        self,
        apikey=settings.TVDB_API_KEY,
        username=settings.TVDB_USERNAME,
        userkey=settings.TVDB_USER_KEY,
    ):
        self.apikey = apikey
        self.username = username
        self.userkey = userkey
        self.domain = 'https://api.thetvdb.com'
        self.token = None
        self.token_set_at = None

    def set_token(self):
        self.token = self.get_new_token()
        self.token_set_at = timezone.now()

    def get_new_token(self):
        payload = {'apikey': self.apikey, 'username': self.username, 'userkey': self.userkey}
        url = f'{self.domain}/login'
        r = requests.post(url, json=payload)
        return r.json()['token']

    def get_auth_headers(self):
        if (self.token is None or self.token_set_at is None)\
                or (time.time() - self.token_set_at.timestamp()) > TOKEN_VALID_TIME:
            logger.debug('Getting a new token')
            self.set_token()
        return dict(Authorization=f'Bearer {self.token}')

    def search_series_list(self, series_name):
        params = dict(name=series_name)
        headers = self.get_auth_headers()
        url = f'{self.domain}/search/series'
        data = json_request(url, params, headers=headers)
        return data

    def get_series_with_id(self, tvdb_id):
        url = f'{self.domain}/series/{tvdb_id}'
        headers = self.get_auth_headers()
        data = json_request(url, headers=headers)
        return data

    def get_season_episode_list(self, tvdb_id, number):
        url = f'{self.domain}/series/{tvdb_id}/episodes/query'
        params = dict(airedSeason=number)
        headers = self.get_auth_headers()
        season_data = []
        data = json_request(url, params=params, headers=headers)
        if data is not None:
            for episode in data:
                episode_data = dict(
                    number=episode['airedEpisodeNumber'],
                    episodeName=episode['episodeName'],
                    firstAired=episode['firstAired'],
                    tvdbID=episode['id'],
                    overview=episode['overview']
                )
                season_data.append(episode_data)
        return season_data

    def get_all_episodes(self, tvdb_id, start_season):
        show = {}
        for i in range(start_season, 100):
            time.sleep(REQUEST_INTERVAL)
            logger.debug(
                f'Requesting season {i} data for show id {tvdb_id}'
            )
            season_data = self.get_season_episode_list(tvdb_id, i)
            if season_data:
                show['Season'+str(i)] = season_data
            else:
                break
        return show
