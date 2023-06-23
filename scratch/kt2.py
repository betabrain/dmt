import kt1

class cqrs(kt1.repository):

    def __init__(self, filepath):
        super().__init__(filepath)
        self.handlers = []
        self.progress = {}

    def since(self, artid=None):
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

    def increment(self):
        for handler in self.handlers:
            for artid in self.since(self.progress.get(handler)):
                art = self.get(artid)
                if isinstance(art, dict) and art.get('_type') == 'cmd':
                    handler(**art.get('_args', {}))
                self.progress[handler] = artid

    def __getattr__(self, name):
        def _command(**kwargs):
            artid = self.__repo.add(dict(
                _type='cmd',
                _name=name,
                _args=kwargs,
                ))
            self.increment()
            return artid
        return _command
