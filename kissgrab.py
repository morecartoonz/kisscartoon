import argparse
import logging
import os
import Queue
import threading,time
import cfscrape
from pySmartDL import SmartDL
import urllib2

from shows import *

logging.basicConfig(level=logging.ERROR, format='[%(levelname)s] : %(message)s')

class Downloader(object):

    def __init__(self, interval=1):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        while dlQueue.not_empty:
            index = dlQueue.get()
            logging.info('Downloader : Grabbed an item. {0} remaining'.format(dlQueue.qsize()))

            path = ".%s%s" % (os.sep, '{title}.mp4'.format(title=foundEpTitles[index]))
            if os.path.isfile(path):
                logging.info("Downloader : The file at %s already exists. Skipping..." % (path))
                foundEpFileStatus[index] = "Grabbed"
                dlQueue.task_done()
            else:
                logging.info('Downloader : Getting {file}'.format(file=foundEpTitles[index]))
                obj = SmartDL(foundEpFilelinks[index], path, progress_bar=False)
                try:
                    obj.start(blocking=True)
                    if obj.isSuccessful():
                        foundEpFileStatus[index] = "Grabbed"
                        logging.info("Downloader : Grabbed '%s' in %s" % (obj.get_dest(), obj.get_dl_time(human=True)))
                        dlQueue.task_done()
                    else:
                        foundEpFilelinks[index] = 'new'
                        logging.info("Downloader : Error grabbing '%s'" % obj.get_dest())
                        dlQueue.task_done()
                        for e in obj.get_errors():
                                logging.error(str(e))
                except KeyboardInterrupt:
                    obj.stop()

            time.sleep(self.interval)

def writeDatFile(foundEpTitles, foundEpLinks, foundEpFilelinks, foundEpFileStatus):
    with open('kissgrab.dat', 'w') as datfile:
        logging.info("writing kissgrab.dat file...")
        for i, val in enumerate(foundEpTitles):
            datfile.write('{eptitle} @ {eplink} @ {filelink} @ {status}\n'.format(eptitle=foundEpTitles[i], eplink=foundEpLinks[i], filelink=foundEpFilelinks[i], status=foundEpFileStatus[i]))
        logging.info("Done!")


parser = argparse.ArgumentParser()
parser.add_argument("show")
parser.add_argument("-l", "--print-links", help="only prints the links. doesn't download the files.", action="store_true")
parser.add_argument("-s", "--save-links", help="saves the links to links.txt", action="store_true")
parser.add_argument("-d", "--save-html", help="outputs a link list to download.html", action="store_true")
parser.add_argument("-g", "--grab-files", help="download the files to the current directory", action="store_true")
parser.add_argument("-q", "--low-quality", help="reduces the quality", action="store_true")
parser.add_argument("-v", "--verbose", help="make kissgrab tell you what it's doing", action="store_true")
args = parser.parse_args()

if args.verbose:
    logging.getLogger().setLevel(logging.INFO)

TIMEOUT = 60 # in seconds
dlQueue = Queue.Queue()
downloader = Downloader()

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
                logging.info('{ep}{msg} ({i})'.format(ep=episode.eptitle.encode('utf-8').ljust(65), msg='found in kissgrab.dat', i=itemNo))
            else:
                foundEpTitles.append(episode.eptitle.encode('utf-8'))
                foundEpLinks.append(episode.sourcelink)
                foundEpFilelinks.append('new')
                foundEpFileStatus.append('new')
                itemNo = foundEpTitles.index(episode.eptitle.encode('utf-8'))
                logging.info('{ep}{msg} ({i})'.format(ep=episode.eptitle.encode('utf-8').ljust(65), msg='added to kissgrab.dat', i=itemNo))
        
        # Now loop through the file links and try to grab from the given EpLink
        logging.info('Looking for file links')
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
                    logging.info("{title}{msg}".format(title=foundEpTitles[i].ljust(65), msg='got a captcha'))
                    writeDatFile(foundEpTitles, foundEpLinks, foundEpFilelinks, foundEpFileStatus)
                    break
                elif args.low_quality:
                    foundEpFilelinks[i] = episode.filelinks[-1].link
                    logging.info("{title}{msg}".format(title=foundEpTitles[i].ljust(65), msg='LQ link found!'))
                    writeDatFile(foundEpTitles, foundEpLinks, foundEpFilelinks, foundEpFileStatus)
                    if args.grab_files:
                        dlQueue.put(i)
                else:
                    foundEpFilelinks[i] = episode.filelinks[0].link
                    logging.info("{title}{msg}".format(title=foundEpTitles[i].ljust(65), msg='HQ link found!'))
                    writeDatFile(foundEpTitles, foundEpLinks, foundEpFilelinks, foundEpFileStatus)
                    if args.grab_files:
                        dlQueue.put(i)
            else:
                if ('Grabbed' in foundEpFileStatus[i]):
                    logging.info("{title}{msg}".format(title=foundEpTitles[i].ljust(65), msg='already have it'))
                else:
                    if args.grab_files:
                        dlQueue.put(i)

        if dlQueue.not_empty:
            logging.info("Waiting for Downloader to exit ...")
        dlQueue.join()

        # Now, write out the current state of the file
        writeDatFile(foundEpTitles, foundEpLinks, foundEpFilelinks, foundEpFileStatus)

      
        # Loop through all the File Links & do what we should
        if args.save_links:
            with open('links.txt', 'w') as linkfile:
                for i,val in enumerate(foundEpFilelinks):
                    linkfile.write(val)
                    linkfile.write('\n')
                linkfile.write('\n')
            logging.info('Saved links to links.txt')

        if args.save_html:
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
            
        if args.print_links:
            for i,val in enumerate(foundEpFilelinks):
                print val
                print '\n'
            print '\n'
