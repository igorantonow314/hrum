import sqlite3 as sl


class DB:
    def __init__(self, db_filename="hrums.db"):
        self.con = sl.connect(db_filename)
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        with self.con:
            self.con.execute(
                """
                CREATE TABLE IF NOT EXISTS videos (
                    video_id TEXT NOT NULL PRIMARY KEY,
                    url TEXT,
                    name TEXT,
                    issue INTEGER,
                    audio_file TEXT,
                    video_date DATE
                );
                """
            )

    def insert_video(
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
                video_id,
                url,
                name,
                issue,
                audio_file,
                video_date,
            )
            return self.con.execute(
                "INSERT INTO videos (video_id, url, name, issue, audio_file, video_date)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                data,
            )

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
