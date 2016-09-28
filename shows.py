from bs4 import BeautifulSoup, SoupStrainer
from episodes import *

class Show(object):
    def __init__(self, show, source):
        self.show = show
        self.source = source
        self.episodes = []

    def is_valid(self):
        raise NotImplementedError()

    def get_episodes(self, session):
        raise NotImplementedError()


class KisscartoonShow(Show):
    BASE_URL = 'http://kisscartoon.me/Cartoon/'

    def is_valid(self):
        if not self.source.startswith(self.BASE_URL):
            return False
        slug = self.source[len(self.BASE_URL):]
        if sum(c is '/' for c in slug) > 1:
            return False
        if '/' in slug:
            if slug[-1] != '/':
                return False
            else:
                slug = slug[:-1]
        self.show = slug
        return self.show.replace('-', '').isalnum()

    def get_episodes(self, session):
        if not self.is_valid():
            return []
        episode_list = session.get(self.source).content
        parsed_list = BeautifulSoup(episode_list, 'html.parser')

        table = parsed_list.find("table", "listing")
        parsed_list = BeautifulSoup(str(table), 'html.parser', parse_only=SoupStrainer('a'))
        for episode in parsed_list:
            self.episodes.append(KisscartoonEpisode(episode.text.strip(),self.show,'http://kisscartoon.me{episode}'.format(episode=episode['href'])))

class KissanimeShow(Show):
    BASE_URL = 'http://kissanime.to/Anime/'
    BASES_URL = 'https://kissanime.to/Anime/'
    def is_valid(self):
        if not self.source.startswith(self.BASE_URL):
            if self.source.startswith(self.BASES_URL):
                self.BASE_URL = self.BASES_URL
            else:
                return False

        slug = self.source[len(self.BASE_URL):]
        if sum(c is '/' for c in slug) > 1:
            return False
        if '/' in slug:
            if slug[-1] != '/':
                return False
            else:
                slug = slug[:-1]
        self.show = slug
        return self.show.replace('-', '').isalnum()

    def get_episodes(self, session):
        if not self.is_valid():
            return []
        episode_list = session.get(self.source).content
        parsed_list = BeautifulSoup(episode_list, 'html.parser')

        table = parsed_list.find("table", "listing")
        parsed_list = BeautifulSoup(str(table), 'html.parser', parse_only=SoupStrainer('a'))
        for episode in parsed_list:
            self.episodes.append(KisscartoonEpisode(episode.text.strip(),self.show,'http://kissanime.to{episode}'.format(episode=episode['href'])))
