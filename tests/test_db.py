import datetime
import os
import sqlite3

import pytest

from db import DB, Video


hrum_for_test_args = {
    "video_id": "w5tXp2wDXUM",
    "url": "https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2",
    "name": "🏡 Лесной дом | ХРУМ или Сказочный детектив (🎧 АУДИО) Выпуск 88",
    "issue": 88,
    "audio_file": None,
    "video_date": "2022-02-19",
}

hrum2_args = {
    "video_id": "uvAK_e8qVaw",
    "url": "https://www.youtube.com/watch?v=uvAK_e8qVaw&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=23",
    "name": "🐈 Кошка, которая гуляла сама по себе | ХРУМ или Сказочный детектив (🎧 АУДИО) Выпуск 67",
    "issue": 67,
    "video_date": datetime.datetime(2021, 2, 13),
}



def test_video_class():
    Video(**hrum_for_test_args)
    Video(**hrum2_args)
    Video(
        "w5tXp2wDXUM",
        "https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2",
    )
    with pytest.raises(TypeError):
        Video()
    with pytest.raises(TypeError):
        Video(name="test", issue=666)
    with pytest.raises(TypeError):
        Video(
            url="https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2"
        )


def test_video_from_url():
    v = Video.from_url(hrum_for_test_args['url'])
    assert v == Video(**hrum_for_test_args)
    v = Video.from_url(hrum2_args['url'])
    assert v == Video(**hrum2_args)


@pytest.fixture
def hrums():
    hrum1 = Video(**hrum_for_test_args)
    hrum2 = Video(**hrum2_args)
    return [hrum1, hrum2]


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
    hrum_for_test_args["issue"] = None
    db.update(Video(**hrum_for_test_args))
    all_rows = list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    assert len(all_rows) == 1
    assert all_rows[0].count(88) == 0
    hrum_for_test_args["issue"] = 88   # restore global variable
    
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
