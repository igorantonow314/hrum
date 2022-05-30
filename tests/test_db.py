import sqlite3

import pytest

from db import create_table_if_not_exists, insert_hrum, update_hrum, get_hrum_by_id


hrum_for_test = {"video_id": "w5tXp2wDXUM", "url": "https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2",
        "name": "🏡 Лесной дом | ХРУМ или Сказочный детектив (🎧 АУДИО) Выпуск 88",
        "issue": 88, "audio_file": None, "video_date": "19.02.2022"}


def test_create_table_if_not_exists():
    create_table_if_not_exists()
    create_table_if_not_exists()


def test_insert_hrum():
    insert_hrum(**hrum_for_test)
    with pytest.raises(sqlite3.IntegrityError):
	    insert_hrum(**hrum_for_test)

def test_update_hrum():
	update_hrum(**hrum_for_test)
	update_hrum(**hrum_for_test)
