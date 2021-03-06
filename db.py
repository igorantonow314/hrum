import dataclasses
import datetime
import logging
import os
import sqlite3 as sl
import typing

from typing import Optional, List, Any

from pytube import YouTube, Playlist
from youtube_dl import YoutubeDL


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class Video:
    video_id: str
    url: str
    name: Optional[str] = None
    issue: Optional[int] = None
    audio_file: Optional[str] = None
    video_date: Optional[datetime.datetime] = None

    def __post_init__(self):
        if (
            not isinstance(self.video_date, datetime.datetime)
            and self.video_date is not None
        ):
            self.video_date = datetime.datetime.fromisoformat(self.video_date)

    @staticmethod
    def _get_primary_key_name(*args):
        return "video_id"

    @staticmethod
    def parse_issue(title):
        if title.lower().find("хрум") >= 0:
            if title.find("Выпуск ") >= 0:
                n = title[title.find("Выпуск ") + len("Выпуск ") :]
                n = int(n)
                return n
            else:
                return -1
        else:
            return None

    @staticmethod
    def from_url(url: str):
        v = YouTube(url)
        video_id = v.video_id
        name = v.title
        video_date = v.publish_date
        audio_file = None
        issue = Video.parse_issue(name)
        return Video(
            video_id=video_id,
            url=url,
            name=name,
            issue=issue,
            audio_file=audio_file,
            video_date=video_date,
        )

    def download_audio(self, cache_dir):
        print("use db.get_hrum_audio_filename() instead")
        fn = os.path.join(cache_dir, "%(id)s")
        with YoutubeDL(
            {"format": "worstaudio", "noplaylist": True, "outtmpl": fn}
        ) as ydl:
            ydl.download([self.url])
        self.audio_file = fn % {"id": self.video_id}


class DB:
    SQL_TYPES = {
        None: "NULL",
        int: "INTEGER",
        float: "FLOAT",
        str: "TEXT",
        bytes: "BLOB",
        datetime.datetime: "DATETIME",
    }

    def __init__(self, db_filename="hrums.db", cache_dir="db_cache", dataclass=Video):
        self.con = sl.connect(db_filename)
        self.dataclass = dataclass
        self.cache_dir = cache_dir
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        sql = """
              CREATE TABLE IF NOT EXISTS videos (
              """
        pk = self.dataclass._get_primary_key_name()
        fields = dataclasses.fields(self.dataclass)

        sql_fields = []
        for field in fields:
            s = f"{field.name} "
            # sqlite3 type
            if o := typing.get_origin(field.type):
                # if field.type is like typing.Optional[int]
                c = list(typing.get_args(field.type))
                if o is typing.Union and c.count(type(None)) > 0:
                    c.remove(type(None))
                    if len(c) != 1 or (
                        len(c) == 1 and c[0] not in self.SQL_TYPES.keys()
                    ):
                        raise TypeError(
                            f"Cannot create table with column type {field.type}"
                        )
                    # typing.Optional[<type>]
                    s += self.SQL_TYPES[c[0]]
                else:
                    raise TypeError(
                        f"Cannot create table with column type {field.type}"
                    )
            elif field.type in self.SQL_TYPES.keys():
                s += self.SQL_TYPES[field.type] + " NOT NULL"
            else:
                raise TypeError(f"Cannot create table with column type {field.type}")
            if field.name == pk:
                s += " PRIMARY KEY"
            sql_fields.append(s)

        sql += ",\n".join(sql_fields)
        sql += "\n);"
        with self.con:
            self.con.execute(sql)

    def insert(self, v) -> None:
        if not isinstance(v, self.dataclass):
            raise TypeError(f"v must be {self.dataclass}")
        sql = "INSERT INTO videos (" + ", ".join(dataclasses.asdict(v).keys())
        sql += ") VALUES (" + ", ".join("?" for _ in dataclasses.astuple(v)) + ")"
        return self.con.execute(sql, dataclasses.astuple(v))

    def update(self, v) -> None:
        if not isinstance(v, self.dataclass):
            raise TypeError(f"v must be {self.dataclass}")
        data_fields = dataclasses.asdict(v)
        data_fields.pop(v._get_primary_key_name())
        sql = "UPDATE videos "
        sql += "SET " + ", ".join((i + "=?" for i in data_fields.keys()))
        sql += "\nWHERE " + v._get_primary_key_name() + "= ?"
        args = list(data_fields.values()) + [getattr(v, v._get_primary_key_name())]
        return self.con.execute(sql, args)

    def get_all(self) -> List[Any]:
        with self.con:
            for row in self.con.execute("SELECT * FROM videos"):
                yield self.dataclass(*row)

    def get_hrums(self) -> List[Video]:
        with self.con:
            sql = "SELECT * FROM videos WHERE issue IS NOT NULL"
            for row in self.con.execute(sql):
                yield self.dataclass(*row)

    def get_last_hrum(self) -> Video:
        sql = (
            "SELECT * FROM videos WHERE issue IS NOT NULL "
            "ORDER BY video_date DESC LIMIT 1"
        )
        with self.con:
            rows = list(self.con.execute(sql))
        if len(rows) == 0:
            return None
        assert len(rows) == 1
        return Video(*rows[0])

    def find_hrums(self, query) -> List[Video]:
        """returns hrums with name that contains substring query"""
        for hrum in self.get_hrums():
            if hrum.name.lower().find(query.lower()) >= 0:
                yield hrum

    def get(self, video_id) -> Video:
        sql = "SELECT * FROM videos WHERE video_id=?"
        logger.debug(f"get({video_id})")
        with self.con:
            rows = list(self.con.execute(sql, [video_id]))
        if len(rows) == 0:
            raise ValueError(f"Record with id {video_id} not found")
        assert len(rows) == 1
        return Video(*rows[0])

    def get_hrum_audio_filename(self, video_id) -> str:
        hrum = self.get(video_id)
        if not hrum.audio_file or os.path.isfile(hrum.audio_file):
            hrum.download_audio(self.cache_dir)
        assert hrum.audio_file is not None
        return hrum.audio_file

    def get_updates(self) -> List[Video]:
        URL = "https://www.youtube.com/playlist?list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB"
        if (lst := self.get_last_hrum()) is not None:
            last_issue = lst.issue
        else:
            last_issue = -1
        p = Playlist(URL)
        for video in p.videos:
            # todo: use video isformation
            try:
                self.get(video.video_id)
            except ValueError:
                hrum = Video.from_url(video.watch_url)
                self.insert(hrum)
                if hrum.issue is not None and hrum.issue > last_issue:
                    yield hrum
