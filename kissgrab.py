import argparse
import logging
import os

import cfscrape
from pySmartDL import SmartDL
import urllib2

from shows import *

logging.basicConfig(level=logging.ERROR, format='[%(levelname)s] : %(message)s')


def download(url, name, quiet=False):
    path = ".%s%s" % (os.sep, name)
    if os.path.isfile(path):
        logging.info("The file at %s already exists. Skipping..." % (path))
        return
    else:
        obj = SmartDL(url, path)
        try:
            obj.start()
        except KeyboardInterrupt:
            obj.stop()

def writeDatFile(foundEpTitles, foundEpLinks, foundEpFilelinks, foundEpFileStatus):
    with open('kissgrab.dat', 'w') as datfile:
        logging.info("writing kissgrab.dat file...")
        for i, val in enumerate(foundEpTitles):
            datfile.write('{eptitle} @ {eplink} @ {filelink} @ {status}\n'.format(eptitle=foundEpTitles[i], eplink=foundEpLinks[i], filelink=foundEpFilelinks[i], status=foundEpFileStatus[i]))
            #print('{eptitle} @ {eplink} @ {filelink}\n'.format(eptitle=foundEpTitles[i], eplink=foundEpLinks[i], filelink=foundEpFilelinks[i]))
        logging.info("Done!")


TIMEOUT = 60 # in seconds

parser = argparse.ArgumentParser()
parser.add_argument("show")
parser.add_argument("-l", "--only-links", help="only prints the links. doesn't download the files.", action="store_true")
parser.add_argument("-s", "--save-links", help="saves the links to links.txt", action="store_true")
parser.add_argument("-q", "--low-quality", help="reduces the quality", action="store_true")
parser.add_argument("-d", "--html", help="outputs a link list to download.html", action="store_true")
parser.add_argument("-v", "--verbose", help="make kissgrab tell you what it's doing", action="store_true")
args = parser.parse_args()

if args.verbose:
    logging.getLogger().setLevel(logging.INFO)

scraper = cfscrape.create_scraper()

for show in Show.__subclasses__():
    showinstance = show(None, args.show)
    if showinstance.is_valid():

        # Get all of the episodes from KissCartoon for the given show
        showinstance.get_episodes(scraper)
        logging.info('Show : {show}'.format(show=showinstance.show))
        
        foundEpTitles = []
        foundEpLinks = []
        foundEpFilelinks = []
        foundEpFileStatus = []
        
        # If we have a kissgrab.dat file, try to load from there
        if os.path.isfile('kissgrab.dat'):
            with open('kissgrab.dat', 'r') as datfile:
                for line in datfile:
                    foundEpTitles.append(line.split('@')[0].strip())
                    foundEpLinks.append(line.split('@')[1].strip())
                    foundEpFilelinks.append(line.split('@')[2].strip())
                    foundEpFileStatus.append(line.split('@')[3].strip())

        # Compare the KissCartoon shows to those from our dat file
        for episode in showinstance.episodes:

            if episode.eptitle.encode('utf-8') in foundEpTitles:
                itemNo = foundEpTitles.index(episode.eptitle.encode('utf-8'))
                logging.info('{ep}\tfound in kissgrab.dat ({i})'.format(ep=episode.eptitle.encode('utf-8'), i=itemNo))
            else:
                foundEpTitles.append(episode.eptitle.encode('utf-8'))
                foundEpLinks.append(episode.sourcelink)
                foundEpFilelinks.append('new')
                foundEpFileStatus.append('new')
                itemNo = foundEpTitles.index(episode.eptitle.encode('utf-8'))
                logging.info('{ep}\tadded to kissgrab.dat ({i})'.format(ep=episode.eptitle.encode('utf-8'), i=itemNo))
        
        # Now loop through the file links and try to grab from the given EpLink
        for i,val in enumerate(foundEpFilelinks):

            if ('captcha' in foundEpFilelinks[i] or 'new' in foundEpFilelinks[i] or foundEpFilelinks[i] == "None"):
                episode.eptitle = foundEpTitles[i]
                episode.sourcelink = foundEpLinks[i]
                try:
                    episode.get_filelinks(scraper, TIMEOUT)
                except:
                    episode.filelinks.append(PlainLink('', 0))
                    
                #if what we get is the captcha, just put "captcha" as the link
                if episode.filelinks[0].quality == 0:
                    foundEpFilelinks[i] = 'captcha'
                    logging.info("{title}\tfinding file links\t...got a captcha".format(title=foundEpTitles[i]))
                    break
                elif args.low_quality:
                    foundEpFilelinks[i] = episode.filelinks[-1].link
                    logging.info("{title}\tfinding file links\tLQ link found!".format(title=foundEpTitles[i]))
                else:
                    foundEpFilelinks[i] = episode.filelinks[0].link
                    logging.info("{title}\tfinding file links\tHQ link found!".format(title=foundEpTitles[i]))
            else:
                logging.info("{title}\tfinding file links\thas a link already".format(title=foundEpTitles[i]))
        print


        # Now, write out the current state of the file
        writeDatFile(foundEpTitles, foundEpLinks, foundEpFilelinks, foundEpFileStatus)
        
        # Loop through all the File Links & do what we should
        if args.save_links:
            with open('links.txt', 'w') as linkfile:
                for i,val in enumerate(foundEpFilelinks):
                    linkfile.write(val)
                    linkfile.write('\n')
            logging.info('Saved links to links.txt')

        if args.html:
            with open('download.html', 'w') as linkfile:
                linkfile.write('<html><head><title>{show}</title></head><body>'.format(show=showinstance.show))
                for i,val in enumerate(foundEpFilelinks):
                    req = urllib2.Request(val)
                    res = urllib2.urlopen(req)
                    finalurl = res.geturl()
                    linkfile.write(
                        '<a href="{link}" download="{file}">{title}</a>'.format(link=finalurl,
                                                                                file=foundEpTitles[i].replace(" ", ""),
                                                                                title=foundEpTitles[i]))
                    linkfile.write('<br>')
                linkfile.write('</body></html>')
            logging.info('Saved links to download.html')
            
        for i,val in enumerate(foundEpFilelinks):
            if args.only_links:
                print val
            elif not args.save_links and not args.html:
                if not ('captcha' in foundEpFilelinks[i] or 'new' in foundEpFilelinks[i] or foundEpFilelinks[i] == "None" or 'Grabbed' in foundEpFileStatus[i]):
                    try:
                        logging.info('Downloading : {file}'.format(file=foundEpTitles[i]))
                        download(val, '{title}.mp4'.format(title=foundEpTitles[i]))
                        foundEpFileStatus[i] = "Grabbed"
                        writeDatFile(foundEpTitles, foundEpLinks, foundEpFilelinks, foundEpFileStatus)
                    except:
                        foundEpFilelinks[i] = 'new'
                        # Now, write out the current state of the file
                        writeDatFile(foundEpTitles, foundEpLinks, foundEpFilelinks, foundEpFileStatus)
