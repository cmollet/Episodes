import os

import pandas as pd

from tvshow.models import Show

cols = [
    'SeriesName',
    'tvdbID',
    'Network',
    'tvdbRating',
    'indicator'
]


genres = [
    'Action',
    'Adventure',
    'Animation',
    'Children',
    'Comedy',
    'Crime',
    'Documentary',
    'Drama',
    'Family',
    'Fantasy',
    'Food',
    'Game Show',
    'Home and Garden',
    'Horror',
    'Mini-Series',
    'Mystery',
    'News',
    'Reality',
    'Romance',
    'Science-Fiction',
    'Soap',
    'Special Interest',
    'Sport',
    'Suspense',
    'Talk Show',
    'Thriller',
    'Travel',
    'Western',
]
module_dir = os.path.dirname(__file__)


def build_training_set():
    tv_df = pd.DataFrame(columns=cols+genres)
    try:
        show_data = Show.objects.all()
        for show in show_data:
            show_genre_list = [0]*28
            show_genre = show.get_genres
            length = len(show_genre)
            for genre in show_genre:
                show_genre_list[genres.index(genre)] = 1.0/length
            show_datas = [
                show.series_name, show.tvdb_id, show.network, int(show.user_rating),
                (float(show.site_rating)**2)*float(show.user_rating)
            ]
            tv_df = tv_df.append(pd.DataFrame([show_datas+show_genre_list], columns=cols+genres))
        extended_tv_df = pd.read_csv(os.path.join(module_dir, 'extra_train_data.csv'))
        extended_tv_df = extended_tv_df.append(tv_df)
        return extended_tv_df
    except:
        return tv_df
