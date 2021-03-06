import datetime
import os
import sqlite3

from itertools import chain
from shutil import rmtree

import pytest

import pytube.exceptions

from db import DB, Video


hrum_attrs_1 = {
    "video_id": "w5tXp2wDXUM",
    "url": "https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2",
    "name": "🏡 Лесной дом | ХРУМ или Сказочный детектив (🎧 АУДИО) Выпуск 88",
    "issue": 88,
    "audio_file": None,
    "video_date": "2022-02-19",
}

hrum_attrs_2 = {
    "video_id": "uvAK_e8qVaw",
    "url": "https://www.youtube.com/watch?v=uvAK_e8qVaw&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=23",
    "name": "🐈 Кошка, которая гуляла сама по себе | ХРУМ или Сказочный детектив (🎧 АУДИО) Выпуск 67",
    "issue": 67,
    "video_date": datetime.datetime(2021, 2, 13),
}

hrums_attrs = [hrum_attrs_1, hrum_attrs_2]


video_attrs_1 = {
    "url": "https://www.youtube.com/watch?v=kJQP7kiw5Fk&list=PL8A83124F1D79BD4F",
    "video_id": "kJQP7kiw5Fk",
    "name": "Luis Fonsi - Despacito ft. Daddy Yankee",
    "audio_file": None,
    "video_date": "2017-01-12",
}

videos_attrs = [video_attrs_1]


def test_video_class():
    for attrs in videos_attrs:
        Video(**attrs)
    for attrs in hrums_attrs:
        Video(**attrs)
    Video(
        "w5tXp2wDXUM",
        "https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2",
    )
    with pytest.raises(TypeError):
        Video()
    with pytest.raises(TypeError):
        Video(name="test", issue=666)
    with pytest.raises(TypeError):
        Video(name="dskldsl", video_date=3.1415)
    with pytest.raises(TypeError):
        Video(
            url="https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2"
        )


@pytest.mark.skip  # slow
def test_video_from_url():
    for attrs in chain(hrums_attrs, videos_attrs):
        v = Video.from_url(attrs["url"])
        assert v == Video(**attrs)
    with pytest.raises(pytube.exceptions.RegexMatchError):
        Video.from_url("some invalid url")


@pytest.mark.skip
def test_video_download_audio(hrums):
    audio_dir = "cache-tests/audio"
    if os.path.exists(audio_dir):
        rmtree(audio_dir)
    for hrum in [hrums[0], hrums[0], hrums[0], hrums[1], hrums[1]]:
        hrum.download_audio(cache_dir=audio_dir)
        assert os.path.isdir(audio_dir)
        assert os.path.isfile(hrum.audio_file)
    h = hrums[0]
    h.download_audio(cache_dir="cache-tests/audio-alternative")
    assert os.path.isdir(audio_dir)
    assert os.path.isfile(hrum.audio_file)


@pytest.fixture
def hrums():
    return [Video(**attrs) for attrs in hrums_attrs]


@pytest.fixture
def db():
    db_name = "database_for_testing-3893832.db"
    if os.path.exists(db_name):
        os.remove(db_name)
    db = DB(db_name)
    assert os.path.exists(db_name)
    return db


def test_create_table_if_not_exists(db):
    # it already has ran in db.__init__(), but anyway
    db.create_table_if_not_exists()
    db.create_table_if_not_exists()


def test_insert(db, hrums):
    db.insert(hrums[0])
    with pytest.raises(sqlite3.IntegrityError):
        db.insert(hrums[0])
    db.insert(hrums[1])
    with pytest.raises(TypeError):
        db.insert(1, 2, 3)
    with pytest.raises(sqlite3.IntegrityError):
        db.insert(Video(None, None, None))
    with pytest.raises(TypeError):
        db.insert(1)
    with pytest.raises(TypeError):
        db.insert({"id": "dldl", "url": "dddld"})
    with pytest.raises(TypeError):
        db.insert(id="dldl", url="dldld")

    all_rows = list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    assert Video(*all_rows[0]) == hrums[1]
    assert Video(*all_rows[1]) == hrums[0]


def test_update(db, hrums):
    db.update(hrums[0])
    assert [] == list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))

    db.insert(hrums[0])
    hrums[0].issue = None
    db.update(hrums[0])
    all_rows = list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    assert len(all_rows) == 1
    assert all_rows[0].count(88) == 0
    hrums[0].issue = 88  # restore global variable

    db.update(hrums[0])
    all_rows = list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    assert len(all_rows) == 1
    assert all_rows[0].count(88) == 1

    db.insert(hrums[1])
    db.update(hrums[1])
    all_rows = list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    assert len(all_rows) == 2
    assert Video(*all_rows[0]) == hrums[1]
    assert Video(*all_rows[1]) == hrums[0]


def test_get_all(db, hrums):
    vl = list(db.get_all())
    assert vl == []
    db.insert(hrums[0])
    db.insert(hrums[1])
    vl = list(db.get_all())
    assert vl == hrums


def test_get_hrums(db, hrums):
    for h in hrums:
        db.insert(h)
    for attrs in videos_attrs:
        db.insert(Video(**attrs))
    hrums_2 = list(db.get_hrums())
    assert sorted(hrums_2, key=lambda x: x.video_id) == sorted(
        hrums, key=lambda x: x.video_id
    )
    hrums_2 = list(db.get_hrums())
    assert sorted(hrums_2, key=lambda x: x.video_id) == sorted(
        hrums, key=lambda x: x.video_id
    )


def test_get_last_hrum(db, hrums):
    db.insert(hrums[1])
    assert db.get_last_hrum() == hrums[1]
    db.insert(hrums[0])
    assert db.get_last_hrum() == hrums[0]


def test_get_last_hrum_2(db, hrums):
    db.insert(hrums[0])
    db.insert(hrums[1])
    assert db.get_last_hrum() == hrums[0]


def test_find_hrums(db, hrums):
    for h in hrums:
        db.insert(h)
    f = list(db.find_hrums("Кошка"))
    assert len(f) == 1
    assert f[0] == hrums[1]
    f = list(db.find_hrums("лЕсНоЙ дОм"))
    assert len(f) == 1
    assert f[0] == hrums[0]
    f = list(db.find_hrums("88"))
    assert len(f) == 1
    assert f[0] == hrums[0]
    f = list(db.find_hrums("хрум"))
    assert len(f) == len(hrums)
    f = list(db.find_hrums("dslkfdsklsfd"))
    assert len(f) == 0


def test_get(db, hrums):
    with pytest.raises(ValueError):
        db.get(hrums[0].video_id)
    db.insert(hrums[0])
    assert hrums[0] == db.get(hrums[0].video_id)
    db.insert(hrums[1])
    assert hrums[0] == db.get(hrums[0].video_id)
    assert hrums[1] == db.get(hrums[1].video_id)
    with pytest.raises(ValueError):
        db.get("invalid id")


@pytest.mark.skip
def test_get_hrum_audio_filename(db, hrums):
    for hrum in [hrums[0], hrums[1]]:
        db.insert(hrum)
        fn = db.get_hrum_audio_filename(hrum.video_id)
        assert os.path.isfile(fn)
        fn = db.get_hrum_audio_filename(hrum.video_id)
        assert os.path.isfile(fn)
    h = hrums[0]
    fn = db.get_hrum_audio_filename(h.video_id)
    os.remove(fn)
    fn = db.get_hrum_audio_filename(h.video_id)
    assert os.path.isfile(fn)
    # TODO: watch for deleting files from temp before test


@pytest.mark.skip  # slow
def test_get_updates(db, hrums):
    db.insert(hrums[1])
    for i, v in enumerate(db.get_updates()):
        assert v.issue > 67
        if i > 4:
            break  # to make test faster
