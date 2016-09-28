from bs4 import BeautifulSoup, NavigableString
import time
from links import *


class Episode(object):
    def __init__(self, eptitle, showname, sourcelink):
        self.eptitle = eptitle
        self.showname = showname
        self.sourcelink = sourcelink
        self.filelinks = None

    def is_valid(self):
        return False

    def get_links(self, session):
        raise NotImplementedError('Cant\'t get Links for generic type Episode!')

    def __repr__(self):
        return '<show : {show}, episode : {episode}, sourcelink : {sourcelink}>'.format(showname=self.showname, episode=self.eptitle, sourcelink=self.sourcelink)


class KisscartoonEpisode(Episode):
    BASE_URL = 'http://kisscartoon.me/Cartoon/'

    def is_valid(self):
        # Basic Data Validation
        if not str(self.sourcelink).startswith(self.BASE_URL):

            return False
        slug = self.sourcelink[len(self.BASE_URL):]
        # Has to be Episode not Show!
        if sum(c is '/' for c in slug) != 1:
            return False
        if slug[-1] == '/':
            return False
        self.eptitle = slug.split('/')[1]
        #self.show = slug.split('/')[0]
        return True

    def get_filelinks(self, session, timeout):
        episode_page = session.get(self.sourcelink).content
        parsed_page = BeautifulSoup(episode_page, 'html.parser')
        captcha = parsed_page.find("div", "g-recaptcha")
        self.filelinks = []
        if captcha != None:
            captchaLink = PlainLink(captcha, 0)
            self.filelinks.append(captchaLink)
            return self.filelinks
        else:
            links = parsed_page.find("select", {"id": "selectQuality"})
            time.sleep(timeout) #put a sleep here to try and avoid the captcha
        
        if links is None:
            raise ValueError('No Episode links found for [{page}]'.format(page=self.source))

        for child in links.children:
            if hasattr(child,'attr'):

                #Gets rsk key (prehashed decryption key)
                rskKey = session.post("http://kisscartoon.me/External/RSK")
                while (rskKey.status_code == 404):
                    rskKey = session.post("http://kisscartoon.me/External/RSK")

                for linktype in Link.__subclasses__():
                    link = linktype(child['value'], child.text, rskKey.content)
                    decoded_link = None
                    if link.is_encoded():
                        try:
                            decoded_link = link.decode()
                        except:
                            continue
                    if decoded_link is None:
                        continue

                    if decoded_link.is_valid():
                        self.filelinks.append(decoded_link)
                        break
        return self.filelinks


class KissanimeEpisode(KisscartoonEpisode):
    BASE_URL = 'http://kissanime.to/Anime/'
