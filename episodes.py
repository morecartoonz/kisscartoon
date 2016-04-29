from bs4 import BeautifulSoup, NavigableString
from links import *


class Episode(object):
    def __init__(self, title, show, source):
        self.title = title
        self.show = show
        self.source = source
        self.links = None

    def is_valid(self):
        return False

    def get_links(self, session):
        raise NotImplementedError('Cant\'t get Links for generic type Episode!')

    def __repr__(self):
        return '<show : {show}, episode : {episode}, source : {source}>'.format(show=self.show, episode=self.title, source=self.source)


class KisscartoonEpisode(Episode):
    BASE_URL = 'http://kisscartoon.me/Cartoon/'

    def is_valid(self):
        # Basic Data Validation
        if not str(self.source).startswith(self.BASE_URL):

            return False
        slug = self.source[len(self.BASE_URL):]
        # Has to be Episode not Show!
        if sum(c is '/' for c in slug) != 1:
            return False
        if slug[-1] == '/':
            return False
        self.title = slug.split('/')[1]
        #self.show = slug.split('/')[0]
        return True

    def get_links(self, session):
        episode_page = session.get(self.source).content
        parsed_page = BeautifulSoup(episode_page, 'html.parser')
        links = parsed_page.find("select", {"id": "selectQuality"})
        if links is None:
            raise ValueError('No Episode links found for [{page}]'.format(page=self.source))

        self.links = []
        for child in links.children:
            if hasattr(child,'attr'):

                for linktype in Link.__subclasses__():
                    link = linktype(child['value'], child.text)
                    decoded_link = None
                    if link.is_encoded():
                        try:
                            decoded_link = link.decode()
                        except:
                            continue
                    if decoded_link is None:
                        continue

                    if decoded_link.is_valid():
                        self.links.append(decoded_link)
                        break
        return self.links


class KissanimeEpisode(KisscartoonEpisode):
    BASE_URL = 'http://kissanime.to/Anime/'
