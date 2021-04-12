from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re

stopWords = "a about above after again against all am an and any are aren't as at be because been before being below between both but by can't cannot could couldn't did didn't do does doesn't doing don't down during each few for from further had hadn't has hasn't have haven't having he he'd he'll he's her here here's hers herself him himself his how how's i i'd i'll i'm i've if in into is isn't it it's its itself let's me more most mustn't my myself no nor not of off on once only or other ought our ours ourselves out over own same shan't she she'd she'll she's should shouldn't so some such than that that's the their theirs them themselves then there there's these they they'd they'll they're they've this those through to too under until up very was wasn't we we'd we'll we're we've were weren't what what's when when's where where's which while who who's whom why why's with won't would wouldn't you you'd you'll you're you've your yours yourself yourselves".replace("'", '').split()


FrequencyDict = {}
visited = set()
subdomainCount = {}

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        super().__init__(daemon=True)
        
    def run(self):
        largest = 0
        Dont = set()
        f = open("DontTry.txt", "r")
        j = f.read()
        for i in j.split(" "):
            Dont.add(i)
        f.close()
        global visited
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                f = open("DontTry.txt", "w+")
                for k in Dont:
                    f.write(str(k) + " ")
                f.close()
                print(len(visited))
                print(largest)
                f = open("Frequency.txt", "w+")
                d_view = [(v,k) for k,v in FrequencyDict.items()]
                d_view.sort(reverse = True)
                for v,k in d_view[:50]:
                    f.write(str(k) + ": " + str(v) + "\n")
                f.close()
                f = open("subdomain.txt", "w+")
                d_view = [(k,v) for k,v in subdomainCount.items()]
                d_view.sort(reverse = True)
                for k,v in d_view:
                    f.write(str(k) + ', ' + str(v) + "\n")
                f.close()
                f = open("OtherStuff.txt", "w+")
                f.write("Length of Crawl: " + len(visited) + "\nSize of the Largest Page: " + str(largest))
                f.close()
                break
            if tbd_url not in Dont:
                resp = download(tbd_url, self.config, self.logger)
                url = urlparse(tbd_url)
                if tbd_url not in visited and resp.status < 400:
                    soup = BeautifulSoup(resp.raw_response.content, features="html.parser")
                    visited.add(tbd_url)
                    for key in (re.sub('[^ a-zA-Z_]', ' ', soup.get_text()).lower()).split():
                        if key not in stopWords and len(key) > 3:
                            if key not in FrequencyDict:
                                FrequencyDict[key] = 1
                            else:
                                FrequencyDict[key] += 1
                    if len(resp.raw_response.content) > largest:
                        largest = len(resp.raw_response.content)
                    if url.hostname in subdomainCount.keys():
                        subdomainCount[url.hostname] += 1
                    else:
                        subdomainCount[url.hostname] = 1
                if resp.status > 400:
                    Dont.add(tbd_url)
                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                scraped_urls = scraper(tbd_url, resp)
                for scraped_url in scraped_urls:
                    self.frontier.add_url(scraped_url)
                self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
