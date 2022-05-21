from functools import lru_cache

from pytube import Channel, YouTube

CHANNEL_URL = "https://www.youtube.com/user/DetiFM/featured"


@lru_cache
def get_all_hrums():
    c = Channel(CHANNEL_URL)
    hrums = {"without num": []}
    for video in c.videos:
        t = video.title
        if t.lower().find("хрум") >= 0:
            if t.lower().find("Выпуск ") >= 0:
                n = t[t.lower.find("Выпуск ") + len("Выпуск ") :]
                n = int(n)
                hrums[n] = video
            else:
                hrums["without num"].append(video)
    return hrums

def get_hrums():
    c = Channel(CHANNEL_URL)
    for video in c.videos:
        t = video.title
        if t.lower().find("хрум") >= 0:
            yield (t, video)


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


def find_hrum_v1(issue: int):
    if type(issue) is not int:
        raise TypeError("issue must be int")
    hrums = get_hrums()
    return hrums.get(issue)


def find_hrum_v2(issue: int):
    for t, v in get_hrums():
        print('processing', t)
        print(parse_num(t))
        if parse_num(t) == issue:
            return v


if __name__ == "__main__":
    print(find_hrum_v2(92).title)
