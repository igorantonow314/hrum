import datetime
import os
import sqlite3

import pytest

from db import DB, Video


hrum_for_test = {
    "video_id": "w5tXp2wDXUM",
    "url": "https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2",
    "name": "🏡 Лесной дом | ХРУМ или Сказочный детектив (🎧 АУДИО) Выпуск 88",
    "issue": 88,
    "audio_file": None,
    "video_date": "19.02.2022",
}

hrum2 = {
    "video_id": "uvAK_e8qVaw",
    "url": "https://www.youtube.com/watch?v=uvAK_e8qVaw&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=23",
    "name": "🐈 Кошка, которая гуляла сама по себе | ХРУМ или Сказочный детектив (🎧 АУДИО) Выпуск 67",
    "issue": 67,
    "video_date": datetime.datetime(2021, 2, 13),
}

hrums = [hrum_for_test, hrum2]


def test_video_class():
    for hrum in hrums:
        Video(**hrum)
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


def test_insert(db):
    db.insert(Video(**hrum_for_test))
    with pytest.raises(sqlite3.IntegrityError):
        db.insert(Video(**hrum_for_test))
    db.insert(Video(**hrum2))
    with pytest.raises(TypeError):
        db.insert(1, 2, 3)
    with pytest.raises(sqlite3.IntegrityError):
        db.insert(Video(None, None, None))
    all_rows = list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    assert all_rows[1] == tuple(hrum_for_test.values())
    assert all_rows[0][:-2] == tuple(hrum2.values())[:-1]
    assert datetime.datetime.fromisoformat(all_rows[0][-1]) == hrum2["video_date"]
    with pytest.raises(TypeError):
        db.insert(1)
    with pytest.raises(TypeError):
        db.insert({"id": "dldl", "url": "dddld"})
    with pytest.raises(TypeError):
        db.insert(id="dldl", url="dldld")


def test_update(db):
    db.update(Video(**hrum_for_test))
    assert [] == list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    db.insert(Video(**hrum_for_test))
    hrum_for_test["issue"] = None
    db.update(Video(**hrum_for_test))
    hrum_for_test["issue"] = 88
    db.update(Video(**hrum_for_test))
    db.insert(Video(**hrum2))
    db.update(Video(**hrum2))
    all_rows = list(db.con.execute("SELECT * FROM videos ORDER BY video_id"))
    assert len(all_rows) == 2
    assert all_rows[0][:-2] == tuple(hrum2.values())[:-1]
    assert datetime.datetime.fromisoformat(all_rows[0][-1]) == hrum2["video_date"]
    assert Video(*all_rows[1]) == Video(**hrum_for_test)


def test_get_videos(db):
    db.insert(Video(**hrum_for_test))
    h = db.get_videos()
    hl = list(h)
    assert len(hl) == 1
    assert hl[0][0] == hrum_for_test["video_id"]
    assert hl[0][1] == hrum_for_test["url"]
    assert hl[0][2] == hrum_for_test["name"]
    assert hl[0][3] == hrum_for_test["issue"]
    assert hl[0][4] == hrum_for_test["audio_file"]
    assert hl[0][5] == hrum_for_test["video_date"]
