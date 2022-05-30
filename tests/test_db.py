import os
import sqlite3

import pytest

from db import DB


hrum_for_test = {
    "video_id": "w5tXp2wDXUM",
    "url": "https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2",
    "name": "🏡 Лесной дом | ХРУМ или Сказочный детектив (🎧 АУДИО) Выпуск 88",
    "issue": 88,
    "audio_file": None,
    "video_date": "19.02.2022",
}


@pytest.fixture
def db():
    db_name = "database_for_testing-3893832.db"
    if os.path.exists(db_name):
        os.remove(db_name)
    db = DB(db_name)
    assert os.path.exists(db_name)
    return db


def test_create_table_if_not_exists(db):
    db.create_table_if_not_exists()
    db.create_table_if_not_exists()


def test_insert_video(db):
    db.insert_video(**hrum_for_test)
    with pytest.raises(sqlite3.IntegrityError):
        db.insert_video(**hrum_for_test)


def test_update_video(db):
    db.update_video(**hrum_for_test)
    db.update_video(**hrum_for_test)
