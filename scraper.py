import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


BlackHole = {}

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    global BlackHole
    MAXVISIT = 20
    nextL = list()
    if resp.status >= 200 and resp.status < 400:
        soup = BeautifulSoup(resp.raw_response.content, features="html.parser")
        URL = urlparse(url)
        for link in soup.find_all('a'):
            f = link.get('href', "")
            if f != "":
                F = urlparse(f)
                if (F.path not in BlackHole.keys() and len(f.split('/')) >= 6) or sum(1 for a,b in zip(F.path, URL.path) if a != b) < 4:
                    BlackHole[F.path] = 0
                if len(f.split('/')) < 6:
                    nextL.append(f)
                elif (len(f.split('/')) >= 6 and len(f.split('/')) < 15) or  sum(1 for a,b in zip(F.path, URL.path) if a != b) < 4:
                    if BlackHole[F.path] <= MAXVISIT:
                        nextL.append(f)
                        BlackHole[F.path] += 1
    return nextL

def is_valid(url):
    global Dont
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|z|ppsx)$", parsed.path.lower()) and not re.search(
            r"boothing|(19|20)\d{2}", parsed.path.lower()) and not not re.search(
            r"\.ics\.uci\.edu/|\.cs\.uci\.edu/|\.informatics\.uci\.edu/|\.stat\.uci\.edu/|today\.uci\.edu/department/information_computer_sciences/", parsed.geturl())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
