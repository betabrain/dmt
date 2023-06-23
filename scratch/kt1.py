import cbor2
import hashlib
import sqlite3
from typeguard import typechecked


class repository(object):

    def __init__(self, filepath):
        self.__db = sqlite3.connect(filepath)
        self.__db.execute("""
            CREATE TABLE IF NOT EXISTS artefact (
                local INTEGER PRIMARY KEY AUTOINCREMENT,
                artid TEXT UNIQUE NOT NULL,
                data BLOB NOT NULL
            );
        """)
        self.__db.commit()

    @typechecked
    def add(self, artefact: object) -> str:
        data = cbor2.dumps(artefact)
        artid = hashlib.sha3_256(data).hexdigest()
        if artid not in self:
            self.__db.execute("""
                INSERT INTO artefact (
                    artid,
                    data
                ) VALUES ( ?, ? );
            """, (artid, data))
            self.__db.commit()
        return artid

    @typechecked
    def get(self, artid: str) -> object:
        sql = "SELECT data FROM artefact WHERE artid=?;"
        for row in self.__db.execute(sql, (artid,)):
            return cbor2.loads(row[0])
        else:
            raise KeyError('no such artefact')

    def __iter__(self):
        for row in self.__db.execute("SELECT artid FROM artefact ORDER BY local;"):
            yield row[0]

    @typechecked
    def since(self, artid: str = None):
        if artid is None:
            return iter(self)
        else:
            sql = """
                SELECT
                    art1.artid
                FROM artefact AS art1
                JOIN artefact AS art2 ON art1.local > art2.local
                WHERE art2.artid=?;
            """
            for row in self.__db.execute(sql, (artid,)):
                yield row[0]

    @typechecked
    def __contains__(self, artid: str) -> bool:
        sql = "SELECT artid FROM artefact WHERE artid=?;"
        for row in self.__db.execute(sql, (artid,)):
            return True
        return False

    @typechecked
    def __len__(self) -> int:
        for row in self.__db.execute("SELECT count(*) FROM artefact;"):
            return row[0]


class cqrs(repository):

    def __init__(self, repo):
        self.__repo = repo
        self.__pos = {}
        self.init()
        self.rebuild()

    def incremental_update(self):
        print('incremental_update')
        for attr in dir(self):
            if attr.startswith('handle_'):
                p = self.__pos.get(attr)
                for artid in self.since(p):
                    cmd = self.__repo.get(artid)
                    if isinstance(cmd, dict) and cmd.get('_type', None) == 'cmd':
                        name = cmd.get('_name')
                        handler = getattr(self, f'handle_{name}')
                        handler(**cmd.get('_args', {}))
                    self.__pos[attr] = artid

    def rebuild(self):
        print('rebuild')
        self.incremental_update()

    def __getattr__(self, name):
        def _command(**kwargs):
            artid = self.__repo.add(dict(
                _type='cmd',
                _name=name,
                _args=kwargs,
                ))
            self.incremental_update()
            return artid
        return _command

    def init(self):
        pass
