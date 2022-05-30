import sqlite3 as sl

con = sl.connect("hrums.db")


def create_table():
    with con:
        con.execute(
            """
			CREATE TABLE videos (
				video_id TEXT NOT NULL PRIMARY KEY,
				url TEXT,
				name TEXT,
				issue INTEGER,
				audio_file TEXT,
				video_date DATE
			);
			"""
        )


def create_table_if_not_exists():
    with con:
        con.execute(
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


def insert_hrum(
    video_id: str,
    url: str,
    name: str,
    issue: int = None,
    audio_file: str = None,
    video_date=None,
):
    with con:
        data = (
            video_id,
            url,
            name,
            issue,
            audio_file,
            video_date,
        )
        return con.execute(
            "INSERT INTO videos (video_id, url, name, issue, audio_file, video_date)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            data,
        )


def update_hrum(
    video_id: str,
    url: str,
    name: str,
    issue: int = None,
    audio_file: str = None,
    video_date=None,
):
    with con:
        data = (
            url,
            name,
            issue,
            audio_file,
            video_date,
            video_id,
        )
        return con.execute(
            """UPDATE videos
            SET url=?, name=?, issue=?, audio_file=?, video_date=?
            WHERE video_id=?""",
            data,
        )



def get_hrum_by_id(video_id: str):
	with con:
		data = con.execute("""
			SELECT video_id, url, name, issue, audio_file, video_date
            FROM videos""")
		data = list(data)
		assert len(data) == 1
		return data[0]



if __name__ == "__main__":
    create_table_if_not_exists()
    update_hrum(
        "w5tXp2wDXUM",
        "https://www.youtube.com/watch?v=w5tXp2wDXUM&list=PL2zdSUwWeOXoyBALahvSq_DsxAFWjHAdB&index=2",
        "test",
    )
    print(get_hrum_by_id("w5tXp2wDXUM"))
    with con:
        data = con.execute("SELECT * FROM videos")
        for row in data:
            print(row)
