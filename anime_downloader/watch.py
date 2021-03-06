from anime_downloader import util, config
from anime_downloader.sites.nineanime import NineAnime

import os
import sys
import pickle
import logging
import click
import warnings
from time import time

# Don't warn if not using fuzzywuzzy[speedup]
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    from fuzzywuzzy import process


class Watcher:
    WATCH_FILE = os.path.join(config.APP_DIR, 'watch.json')

    def __init__(self):
        pass

    def new(self, url):
        anime = AnimeInfo(url, timestamp=time())

        self._append_to_watch_file(anime)

        logging.info('Added {:.50} to watch list.'.format(anime.title))

    def list(self):
        animes = self._read_from_watch_file()

        click.echo('{:>5} | {:^35} | {:^8} | {:^10}'.format(
            'SlNo', 'Name', 'Eps', 'Type'
        ))
        click.echo('-'*65)
        fmt_str = '{:5} | {:35.35} |  {:3}/{:<3} | {meta:10.10}'

        for idx, anime in enumerate(animes):
            meta = anime.meta
            click.echo(fmt_str.format(idx+1, anime.title,
                                      *anime.progress(),
                                      meta=meta.get('Type', '')))

    def get(self, anime_name):
        animes = self._read_from_watch_file()

        if isinstance(anime_name, int):
            return animes[anime_name]

        match = process.extractOne(anime_name, animes, score_cutoff=40)
        if match:
            anime = match[0]

            if (time() - anime._timestamp) > 4*24*60*60:
                anime = self.update_anime(anime)
            return anime

    def update_anime(self, anime):
        anime_name = anime.title
        anime.getEpisodes()
        anime.title = anime_name
        self.update(anime)
        return anime

    def add(self, anime):
        self._append_to_watch_file(anime)

    def remove(self, anime):
        anime_name = anime.title
        animes = self._read_from_watch_file()
        animes = [anime for anime in animes if anime.title != anime_name]
        self._write_to_watch_file(animes)

    def update(self, changed_anime):
        animes = self._read_from_watch_file()
        animes = [anime for anime in animes
                  if anime.title != changed_anime.title]
        animes = [changed_anime] + animes
        self._write_to_watch_file(animes)

    def _append_to_watch_file(self, anime):
        if not os.path.exists(self.WATCH_FILE):
            self._write_to_watch_file([anime])
            return

        with open(self.WATCH_FILE, 'rb') as watch_file:
            data = pickle.load(watch_file)

        data = [anime] + data
        self._write_to_watch_file(data)

    def _write_to_watch_file(self, animes):
        with open(self.WATCH_FILE, 'wb') as watch_file:
            pickle.dump(animes, watch_file)

    def _read_from_watch_file(self):
        if not os.path.exists(self.WATCH_FILE):
            logging.error('Add something to watch list first.')
            sys.exit(1)

        with open(self.WATCH_FILE, 'rb') as watch_file:
            data = pickle.load(watch_file)

        return data


class AnimeInfo(NineAnime):
    def __init__(self, *args, **kwargs):
        self.episodes_done = kwargs.pop('episodes_done', 0)
        self._timestamp = kwargs.pop('timestamp')

        super(NineAnime, self).__init__(*args, **kwargs)

    def progress(self):
        return (self.episodes_done, len(self))
