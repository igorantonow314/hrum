from functools import lru_cache
import json
import os
from typing import Optional

from pytube import Channel, YouTube, Playlist

CHANNEL_URL = "https://www.youtube.com/user/DetiFM/featured"
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB"
DEFAULT_CONF = 'scan.conf'


def parse_num(title: str) -> int:
    if title.lower().find("хрум") >= 0:
        if title.find("Выпуск ") >= 0:
            n = title[title.find("Выпуск ") + len("Выпуск ") :]
            n = int(n)
            return n
        else:
            return -1
    else:
        return None


def get_last_hrum():
    c = Channel(CHANNEL_URL)
    for v in c.videos:
        t = get_title(v)
        if t.lower().find("хрум") >= 0:
            return v


def get_hrums():
    c = Channel(CHANNEL_URL)
    for video in c.videos:
        t = get_title(video)
        if t.lower().find("хрум") >= 0:
            yield (t, video)


def load_conf(conf=DEFAULT_CONF):
    if not os.path.exists(conf):
        save_conf({'version': 0.1}, conf)
    with open(conf, 'r') as f:
        return json.load(f)


def save_conf(data, conf=DEFAULT_CONF):
    with open(conf, 'w') as f:
        json.dump(data, f)


def get_last_hrum_num(conf=DEFAULT_CONF):
    c = load_conf(conf)
    return c.get('last_hrum_num') or -1


def update_last_hrum_num(new_n, conf=DEFAULT_CONF):
    c = load_conf(conf)
    n = c.get('last_hrum_num') or -1
    c['last_hrum_num'] = max(n, new_n)
    save_conf(c, conf)



def get_updates(conf=DEFAULT_CONF):
    c = load_conf(conf)
    n = get_last_hrum_num()
    for t, v in get_hrums():
        if parse_num(t) > n:
            update_last_hrum_num(parse_num(t))
            yield t, v


def get_title(vid: Optional[YouTube]=None, url: Optional[str]=None):
    if url:
        vid = YouTube(url)
    url = vid.watch_url
    c = load_conf()
    if c.get('videos') is None:
        c['videos'] = dict()
    if r := c['videos'].get(url):
        if title := r.get('title'):
            return title
    c['videos'][url] = {'title': vid.title}
    save_conf(c)
    return c['videos'][url]['title']


if __name__ == "__main__":
    for t, v in get_updates():
        print(t, v.publish_date)
