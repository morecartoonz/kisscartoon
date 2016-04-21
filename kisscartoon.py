__author__ = 'Jan'
from bs4 import BeautifulSoup
import cfscrape
from pySmartDL import SmartDL
import os.path
import argparse
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import binascii
import base64
import string

class KissEnc:
    def __init__(self):
        a = "WrxLl3rnA48iafgCy"
        b = "a5e8d2e9c1721ae0e84ad660c472c1f3"
        c = "CartKS$2141#"
        self.derived_key = PBKDF2(a,c, dkLen=32, count=1000)
        self.derived_key = binascii.hexlify(self.derived_key)[0:32]
        self.cipher = AES.new(self.derived_key.decode('hex'), AES.MODE_CBC, b.decode('hex'))

    def decrypt(self, data):
        val = self.cipher.decrypt(base64.b64decode(data))
        val = self.decode(val)
        printable = set(string.printable)
        val = filter(lambda x: x in printable, val)
        val = 'https://redirect%s' % val[val.index('or.googlevideo.com'):]
        return self.ensure_unicode(val)


    def decode(self, text, k = 16):
        '''
        Remove the PKCS#7 padding from a text string

        Made by https://gist.github.com/chrix2
        '''
        nl = len(text)
        val = int(binascii.hexlify(text[-1]), 16)
        if val > k:
            raise ValueError('Input is not padded or padding is corrupt')

        l = nl - val
        return text[:l]

    def ensure_unicode(self,v):
        if isinstance(v, str):
            v = v.decode('utf8')
        return unicode(v)


decoder = KissEnc()

def get_episodes(url, kissanime=False):
    html = scraper.get(url).content
    soup = BeautifulSoup(html, "lxml")

    table = soup.find("table", "listing")

    tablesoup = BeautifulSoup(str(table), "lxml")

    links = []

    for link in tablesoup.findAll('a'):
        if kissanime:
            links.append(u"%s%s" % ("http://kissanime.com", link.get('href')))
        else:
            links.append(u"%s%s" % ("http://kisscartoon.me", link.get('href')))
    return links


def get_episode(url, quiet=False, quality=False):
    html = scraper.get(url).content
    soup = BeautifulSoup(html, "lxml")
    link = soup.find("select", {"id": "selectQuality"})
    valuesoup = BeautifulSoup(str(link), "lxml")
    dlinks = []
    quali = []
    for src in valuesoup.findAll('option'):
        quali.append(src.text)
        dlinks.append(decoder.decrypt(src.get('value')))
    if not quiet:
        if quality:
            print("Quality : " + quali[len(quali)-1])
        else:
            print("Quality : " + quali[0])
    return dlinks


def download(url, name, quiet = False):
    path = ".%s%s" % (os.sep, name)
    if os.path.isfile(path):
        if not quiet:
            print "Skipping %s" % name
        return
    else:
        obj = SmartDL(url, path)
        try:
            obj.start()
        except KeyboardInterrupt:
            obj.stop()



parser = argparse.ArgumentParser()
parser.add_argument("show")
parser.add_argument("-l","--only-links", help="only print's the links. doesn't download the files.", action="store_true")
parser.add_argument("-s","--save-links", help="saves the links to links.txt", action="store_true")
parser.add_argument("-a","--low-quality", help="reduces the quality", action="store_true")
parser.add_argument("-q","--quiet", help="shut's up", action="store_true")
args = parser.parse_args()


scraper = cfscrape.create_scraper()

show = args.show

showname = show.split("/")[-1]
if not args.quiet:
    print("Serie : %s" % showname)

links = []

for episode in list(reversed(get_episodes(show, "kissanime" in show))):
    episodename = episode.split("/")[-1].split("?")[0] + ".mp4"
    if not args.quiet:
        print "Episode : %s" % episodename
    qualitys = get_episode(episode, args.quiet, args.low_quality)
    if args.low_quality:
        link = qualitys[len(qualitys)-1]
    else:
        link = qualitys[0]

    if args.only_links:
        print(link)
    else:
        download(link, "%s_%s" % (showname, episodename), args.quiet)

    if args.save_links:
        links.append(link)
    print("\n")
if args.save_links:
    with open('links.txt', 'a') as file:
        for link in links:
            file.write("%s" % (link) )


