import logging
import time
import unicodedata
import nltk
from urllib.request import urlopen
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from collections import defaultdict
from string import punctuation
from bs4 import BeautifulSoup
from flask import Flask
from heapq import nlargest

app = Flask(__name__)
url = "https://www.ft.com"
cache_timeout = 600
link_cache = list()


def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    _logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    _logger.setLevel(logging.INFO)
    return _logger


logger = get_module_logger('tweeter')


def get_links():
    page = urlopen(url).read()
    soup = BeautifulSoup(page, 'lxml')
    divs = soup.findAll('div', {'data-trackable': 'popular'})
    links = []
    if len(divs) == 0:
        logger.error('No popular divs found')
    for div in divs:
        popular_links = div.findAll('a')
        if len(popular_links) == 0:
            logger.error('No popular links found')
        for link in popular_links:
            links.append(link['href'])
    return links


def get_text(href):
    page = urlopen(url + href)
    soup = BeautifulSoup(page, "lxml")
    div = soup.find('div', {'class': 'article__content-body n-content-body js-article__content-body'})
    if div is None:
        logging.error('No content body div found: ' + href)
        return None
    paras = div.findAll('p')
    text = ''
    for para in paras:
        text += para.text
    return text


def time_expire_cache():
    now = time.time()
    expire_time = now - cache_timeout
    for _link in link_cache:
        if _link[1] < expire_time:
            logger.info('Expiring: %s' % _link[0])
            link_cache.remove(_link)


def summarise(text, n):
    sentences = sent_tokenize(text)

    assert n <= len(sentences)
    word_sent = word_tokenize(text.lower())
    _stopwords = set(stopwords.words('english') + list(punctuation))

    word_sent = [word for word in word_sent if word not in _stopwords]
    freq = FreqDist(word_sent)

    ranking = defaultdict(int)

    for i, sent in enumerate(sentences):
        for w in word_tokenize(sent.lower()):
            if w in freq:
                ranking[i] += freq[w]

    sentences_idx = nlargest(n, ranking, key=ranking.get)
    return [unicodedata.normalize('NFKC', sentences[j]) for j in sorted(sentences_idx)]


@app.route('/')
def tweet():
    logger.info('received request')
    links = get_links()
    if len(links) == 0:
        logger.error('No links found')
        return 'No links found'
    time_expire_cache()
    for link in links:
        logger.debug('Link found: ' + link)
        in_cache = False
        for _link in link_cache:
            if _link[0] == link:
                in_cache = True
                break
        if not in_cache:
            link_cache.append((link, time.time()))
            text = get_text(link)
            if text is not None:
                summary_sentences = summarise(text, 3)
                for summary_sentence in summary_sentences:
                    logger.info(summary_sentence)
    return 'success'
