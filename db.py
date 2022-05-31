import dataclasses
import datetime
import sqlite3 as sl
import typing

from typing import Optional


@dataclasses.dataclass
class Video:
    video_id: str
    url: str
    name: Optional[str] = None
    issue: Optional[int] = None
    audio_file: Optional[str] = None
    video_date: Optional[datetime.datetime] = None

    def _get_primary_key_name():
        return "video_id"


class DB:
    SQL_TYPES = {
        None: "NULL",
        int: "INTEGER",
        float: "FLOAT",
        str: "TEXT",
        bytes: "BLOB",
        datetime.datetime: "DATETIME",
    }

    def __init__(self, db_filename="hrums.db", dataclass=Video):
        self.con = sl.connect(db_filename)
        self.dataclass = dataclass
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

    def insert(self, v: Video) -> None:
        if not isinstance(v, self.dataclass):
            raise TypeError("v must be Video")
        sql = "INSERT INTO videos (" + ", ".join(dataclasses.asdict(v).keys())
        sql += ") VALUES (" + ", ".join("?" for _ in dataclasses.astuple(v)) + ")"
        return self.con.execute(sql, dataclasses.astuple(v))

    def update_video(
        self,
        video_id: str,
        url: str,
        name: str,
        issue: int = None,
        audio_file: str = None,
        video_date=None,
    ):
        with self.con:
            data = (
                url,
                name,
                issue,
                audio_file,
                video_date,
                video_id,
            )
            return self.con.execute(
                """UPDATE videos
                SET url=?, name=?, issue=?, audio_file=?, video_date=?
                WHERE video_id=?""",
                data,
            )

    def get_video_by_id(self, video_id: str):
        with self.con:
            data = self.con.execute(
                """
                SELECT video_id, url, name, issue, audio_file, video_date
                FROM videos"""
            )
            data = list(data)
            assert len(data) == 1
            return data[0]

    def get_videos(self):
        with self.con:
            data = self.con.execute("""SELECT * FROM videos""")
            return data
