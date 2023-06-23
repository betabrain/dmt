import sqlite3
import uuid


class db(object):

    def __init__(self):
        self.__sqlite = sqlite3.connect(":memory:")
        self.__sqlite.execute(
            """
            CREATE TABLE IF NOT EXISTS t_entities (
                eid INTEGER PRIMARY KEY NOT NULL,
                annotation
            );
        """
        )
        self.__sqlite.execute(
            """
            CREATE TABLE IF NOT EXISTS t_keys (
                kid INTEGER PRIMARY KEY NOT NULL,
                key
            );
        """
        )
        self.__sqlite.execute(
            """
            CREATE TABLE IF NOT EXISTS t_values (
                vid INTEGER PRIMARY KEY NOT NULL,
                value
            );
        """
        )
        self.__sqlite.execute(
            """
            CREATE TABLE IF NOT EXISTS t_records (
                eid INTEGER,
                kid INTEGER,
                vid INTEGER,
                PRIMARY KEY (eid, kid, vid),
                FOREIGN KEY (eid) REFERENCES t_entities (eid),
                FOREIGN KEY (kid) REFERENCES t_keys (kid),
                FOREIGN KEY (vid) REFERENCES t_values (vid)
            );
        """
        )
        self.__sqlite.execute(
            """
            CREATE VIEW IF NOT EXISTS complete_view AS
                SELECT eid, kid, vid, key, value
                FROM t_records
                NATURAL JOIN t_keys
                NATURAL join t_values
                ORDER BY eid, key, value;
        """
        )

    def debug(self):
        for i, row in enumerate(self.__sqlite.execute("SELECT * FROM complete_view;")):
            print(i, *row)

    def add(self, **kvs):
        ann = str(uuid.uuid4())
        self.__sqlite.execute("insert into t_entities (annotation) values (?);", (ann,))
        eid = list(
            self.__sqlite.execute(
                "select eid from t_entities where annotation=?;", (ann,)
            )
        )[
            0
        ][
            0
        ]
        for k, v in kvs.items():
            self.__sqlite.execute(
                "insert or ignore into t_keys (key) values (?);", (k,)
            )
            self.__sqlite.execute(
                "insert or ignore into t_values (value) values (?);", (v,)
            )


if __name__ == "__main__":
    d = db()
    d.add(user="donald", password="duck")
    d.debug()
