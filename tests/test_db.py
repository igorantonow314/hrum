import datetime
import os
import sqlite3

import pytest

from db import DB, Video, Hrum


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
    "video_date": "2017-01-12"
}

video_attrs_2 = {
    "video_id": "w5tXp2wDXUM",
    "url": "https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2",
    "name": "🏡 Лесной дом | ХРУМ или Сказочный детектив (🎧 АУДИО) Выпуск 88",
    "audio_file": None,
    "video_date": datetime.datetime(2022, 2, 19),
}

videos_attrs = [video_attrs_1, video_attrs_2]



def test_video_class():
    for attrs in videos_attrs:
        Video(**attrs)
    Video(
        "w5tXp2wDXUM",
        "https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2",
    )
    with pytest.raises(TypeError):
        Video()
    with pytest.raises(TypeError):
        Video(name="test", video_date=3.1415926)
    with pytest.raises(TypeError):
        Video(
            url="https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2"
        )


def test_video_from_url():
    for attrs in videos_attrs:
        v = Video.from_url(attrs['url'])
        assert v == Video(**attrs)


def test_hrum_class():
    for attrs in hrums_attrs:
        h = Hrum(**attrs)


@pytest.fixture
def db(request):
    db_name = "database_for_testing-3893832.db"
    if os.path.exists(db_name):
        os.remove(db_name)
    if request.param == "Video":
        db = DB(db_name, dataclass=Video)
    elif request.param == "Hrum":
        db = DB(db_name, dataclass=Hrum)
    else:
        raise ValueError(request.param)
    assert os.path.exists(db_name)
    return db


@pytest.fixture
def dataclass_ex(request):
    if request.param == "videos":
        return [Video(**attrs) for attrs in videos_attrs]
    if request.param == "hrums":
        return [Hrum(**attrs) for attrs in hrums_attrs]
    raise ValueError(s)


@pytest.mark.parametrize("db", ["Video", "Hrum"], indirect=True)
def test_db_create_table_if_not_exists(db):
    # it already has ran in db.__init__(), but anyway
    db.create_table_if_not_exists()
    db.create_table_if_not_exists()


@pytest.mark.parametrize("db, dataclass_ex", [("Video", "videos"), ("Hrum", "hrums")], indirect=True)
def test_db_insert(db, dataclass_ex):
    db.insert(dataclass_ex[0])
    with pytest.raises(sqlite3.IntegrityError):
        db.insert(dataclass_ex[0])
    db.insert(dataclass_ex[1])
    with pytest.raises(TypeError):
        db.insert(1, 2, 3)
    with pytest.raises(TypeError):
        db.insert(1)
    with pytest.raises(TypeError):
        db.insert({"id": "dldl", "url": "dddld"})
    with pytest.raises(TypeError):
        db.insert(id="dldl", url="dldld")
    
    for de in dataclass_ex[2:]:
        db.insert(de)
    all_rows = list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    d = sorted(dataclass_ex, key=lambda x: x.url)
    assert len(d) == len(all_rows)
    for row, de in zip(all_rows, d):
        assert type(de)(*row) == de

@pytest.mark.parametrize("db, dataclass_ex", [("Video", "videos"), ("Hrum", "hrums")], indirect=True)
def test_db_update(db, dataclass_ex):
    db.update(dataclass_ex[0])
    assert [] == list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    
    db.insert(dataclass_ex[0])
    dataclass_ex[0].audio_file = "some_file_39393.mp3"
    db.update(dataclass_ex[0])
    all_rows = list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    assert len(all_rows) == 1
    assert all_rows[0].count("some_file_39393.mp3") == 1
    
    dataclass_ex[0].audio_file = None
    db.update(dataclass_ex[0])
    all_rows = list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    assert len(all_rows) == 1
    assert all_rows[0].count("some_file_39393.mp3") == 0
    
    db.insert(dataclass_ex[1])
    db.update(dataclass_ex[1])
    all_rows = list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    assert len(all_rows) == 2
    d = sorted(dataclass_ex[:2], key=lambda x: x.url)
    for row, de in zip(all_rows, d):
        assert type(de)(*row) == de


@pytest.mark.parametrize("db, dataclass_ex", [("Video", "videos"), ("Hrum", "hrums")], indirect=True)
def test_db_get_all(db, dataclass_ex):
    vl = list(db.get_all())
    assert vl == []
    db.insert(dataclass_ex[0])
    db.insert(dataclass_ex[1])
    vl = list(db.get_all())
    assert vl == dataclass_ex
